import errno
import json
import select
import socketserver
import threading
import socket
from absl import app, flags
import socket
import sys


port = 9134
ip = '127.0.0.1'
socket_buffer = None
roomCnt = 0
roomList = []
clientList = []
room_members = []



def on_sc_name(msg, client):
  global roomCnt
  global roomList
  global clientList
  for i in roomList:
    if i['members'].index(client['name']) != -1:
      if (i['roomId'] == client['roomNum']):
        i['members'].remove(client['name'])
        i['members'].append(msg['name'])
  client['name'] = msg['name']
  clientList.append(client)
  
  send_message={
    "type" : "SCSystemMessage",
    "text" : f'이름이 {client["name"]}으로 변경되었습니다.'
  }
  return send_message

def on_sc_rooms_result(msg, client):
  send_message={
    "type": "SCRoomsResult",
    "rooms": roomList
  }
  return send_message

def on_sc_create(msg, client):
  global roomCnt
  global roomList
  global clientList
  roomCnt = roomCnt + 1
  client['roomNum'] = roomCnt
  client['status'] = "inRoom"
  room_members.append(client['name'])
  room = {
    "roomId" : roomCnt,
    "title": msg['title'],
    "members": room_members
  }
  roomList.append(room)
  title = room['title']

  send_message={
    "type" : "SCSystemMessage",
    "text": f'방제 {title} 방에 입장했습니다.'
  }
  tmp = room['roomId']
  print(f'방 [{tmp}]: 생성, 방제 {title}')
  return send_message

def on_sc_join_room(msg, client):
  global roomCnt
  global roomList
  global clientList
  roomList[msg['roomID']].append(client)
  title = roomList[msg['title']]
  client['status'] = "inRoom"
  send_message = {
    "type" : "SCSystemMessage",
    "text" : f'방제 {title} 방에 입장했습니다.'
  }
  return send_message

def on_sc_leave_room(msg, client):
  global roomCnt
  global roomList
  global clientList
  print(clientList)
  for r in roomList:
    print(r)
    if (r['roomId'] == client["roomNum"]):
      title = r['title']
      r['members'].remove(client['name'])
      room_members.remove(client['name'])
      client['status'] = "notRoom"
    if (r['members'] == []):
      tmp = r['roomId']
      print(f'방[{tmp}] 명시적 /leave 명령으로 인한 방폭')
      roomList.clear()
  send_message = {
    "type" : "SCSystemMessage",
    'text': f'방제 {title} 대화 방에서 퇴장했습니다.'
  }
  return send_message

def on_sc_shutdown(msg, client):
  print("shutdown 함수 진입")
  client_socket.close()
  server_socket.close()

def on_sc_chat(msg, client):
  global roomCnt
  global roomList
  global clientList
  print(client)
  name = client['name']
  message = msg['text']
  if (client['status'] == "notRoom"):
    send_message = {
      "type" : "SCSystemMessage",
      "text": "현재 대화방에 들어가 있지 않습니다."
    }
  else:
    send_message={
      "type": "SCChat",
      "text": f'[{name}] {message}',
      "member": client['name']
    }
    print(client)
  return send_message


json_message_handlers = {
  'CSName' : on_sc_name,
  'CSCreateRoom' : on_sc_create,
  'CSJoinRoom' : on_sc_join_room,
  'CSLeaveRoom' : on_sc_leave_room,
  'CSRooms': on_sc_rooms_result,
  'CSChat': on_sc_chat,
  'CSShutdown': on_sc_shutdown
}


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', port))
server_socket.listen()

while True:
  client_socket, address = server_socket.accept()
  print(f'Connected to {address}')

  while True:
    received_buffer = client_socket.recv(65535)
    if not socket_buffer:
      socket_buffer = received_buffer
    else:
      socket_buffer += received_buffer

    current_message_len = int.from_bytes(socket_buffer[0:2], byteorder='big')
    socket_buffer = socket_buffer[2:]

    serialized = socket_buffer[:current_message_len]
    socket_buffer = socket_buffer[current_message_len:]
    current_message_len = None

    msg = json.loads(serialized)
    msg_type = msg.get('type', None)

    client = {
      "name" : address,
      "status" : "notRoom",
      "roomNum" : roomCnt
    }

    if msg_type in json_message_handlers:
      print(msg_type)
      send_message = json_message_handlers[msg_type](msg, client)
      clientList.append(client)
    else:
      send_message={
        "type": "SCSystemMessage",
        "text": "없는 타입입니다"
      }
    serialized = bytes(json.dumps(send_message, ensure_ascii = False), encoding='UTF-8')
    send_message = json.dumps(send_message, ensure_ascii = False)

    to_send = len(serialized)
    to_send_big_endian = int.to_bytes(to_send, byteorder='big', length=2)
    serialized = to_send_big_endian + serialized

    offset = 0
    attempt = 0
    while offset < len(serialized):
        num_sent = client_socket.send(serialized[offset:])
        if num_sent <= 0:
          print("asdf")
        offset += num_sent

#!/usr/bin/python3
from flask import Flask
from flask import jsonify
from flask import request
from flask import make_response

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    data = {
        'method': request.method,
        'arg1': int(request.get_json().get('arg1', 0)),
        'arg2': int(request.get_json().get('arg2', 0)),
        'op': request.get_json().get('op', ''),
    }

    if(data.get('op') == '+'):
        result = jsonify(data.get('arg1') + data.get('arg2'))
        resp = make_response(result, 200)
    elif(data.get('op') == '*'):
        result = jsonify(data.get('arg1') * data.get('arg2'))
        resp = make_response(result, 200)
    elif(data.get('op') == '-'):
        result = jsonify(data.get('arg1') - data.get('arg2'))
        resp = make_response(result, 200)
    else:
        resp = make_response(result, 404)

    return resp
    # method =  request.method,
    # arg1 = request.args.get_json().get('arg1')
    # arg2 = request.get_json().get('arg2')
    # op = request.get_json().get('op')


   

    # 'name': request.args.get('name', default='이름이 없는자'),
    # 'client' : request.headers['User-Agent'],
    # 'key1' : request.get_json().get('key1', 'No key')
    # return f'{arg1} {op} {arg2}'# = {result}''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9134)

from http import HTTPStatus
import random
import requests
import json
import mysql.connector
import urllib

from flask import abort, Flask, make_response, render_template, Response, redirect, request

mydb = mysql.connector.connect(
    host="43.202.246.165",
    user="root",
    password="0526",
    database="naver_login"
)


app = Flask(__name__)


naver_client_id = 'QINH29pCOxZJ82zkR5Ub'
naver_client_secret = 'n5Z7aQrCon'
naver_redirect_uri = 'http://60212245-lb-494944562.ap-northeast-2.elb.amazonaws.com/memo/auth'
'''  
  본인 app 의 것으로 교체할 것.
  여기 지정된 url 이 http://localhost:8000/auth 처럼 /auth 인 경우
  아래 onOAuthAuthorizationCodeRedirected() 에 @app.route('/auth') 태깅한 것처럼 해야 함
'''


@app.route('/')

def home():
    # 쿠키를 통해 이전에 로그인 한 적이 있는지를 확인한다.
    # 이 부분이 동작하기 위해서는 OAuth 에서 access token 을 얻어낸 뒤
    # user profile REST api 를 통해 유저 정보를 얻어낸 뒤 'userId' 라는 cookie 를 지정해야 된다.
    # (참고: 아래 onOAuthAuthorizationCodeRedirected() 마지막 부분 response.set_cookie('userId', user_id) 참고)
    userId = request.cookies.get('userId', default=None)
    name = None

    ####################################################
    # TODO: 아래 부분을 채워 넣으시오.
    #       userId 로부터 DB 에서 사용자 이름을 얻어오는 코드를 여기에 작성해야 함

    # MySQL에서 유저 정보 조회
    mydb.reconnect()
    cursor = mydb.cursor(buffered=True)
    query = "SELECT * FROM user_table WHERE userID = %s"
    cursor.execute(query, (userId,))
    user = cursor.fetchone()
    if user:
        name = user[1]
    cursor.close()


    ####################################################


    # 이제 클라에게 전송해 줄 index.html 을 생성한다.
    # template 로부터 받아와서 name 변수 값만 교체해준다.
    return render_template('index.html', name=name)


# 로그인 버튼을 누른 경우 이 API 를 호출한다.
# OAuth flow 상 브라우저에서 해당 URL 을 바로 호출할 수도 있으나,
# 브라우저가 CORS (Cross-origin Resource Sharing) 제약 때문에 HTML 을 받아온 서버가 아닌 곳에
# HTTP request 를 보낼 수 없는 경우가 있다. (예: 크롬 브라우저)
# 이를 우회하기 위해서 브라우저가 호출할 URL 을 HTML 에 하드코딩하지 않고,
# 아래처럼 서버가 주는 URL 로 redirect 하는 것으로 처리한다.
#
# 주의! 아래 API 는 잘 동작하기 때문에 손대지 말 것
@app.route('/login')
def onLogin():
    params={
            'response_type': 'code',
            'client_id': naver_client_id,
            'redirect_uri': naver_redirect_uri,
            'state': random.randint(0, 10000)
        }
    urlencoded = urllib.parse.urlencode(params)
    url = f'https://nid.naver.com/oauth2.0/authorize?{urlencoded}'
    print("login 창 진입")
    return redirect(url)

# 아래는 Redirect URI 로 등록된 경우 호출된다.
# 만일 본인의 Redirect URI 가 http://localhost:8000/auth 의 경우처럼 /auth 대신 다른 것을
# 사용한다면 아래 @app.route('/auth') 의 내용을 그 URL 로 바꿀 것
@app.route('/auth')
def onOAuthAuthorizationCodeRedirected():
    # TODO: 아래 1 ~ 4 를 채워 넣으시오.
    # 1. redirect uri 를 호출한 request 로부터 authorization code 와 state 정보를 얻어낸다.
    code = request.args.get('code') # authorization code 추출
    state = request.args.get('state') # state 정보 추출


    # 2. authorization code 로부터 access token 을 얻어내는 네이버 API 를 호출한다.
    token_request = requests.get(f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={naver_client_id}&client_secret={naver_client_secret}&code={code}&state={state}")
    token_json = token_request.json()
    access_token = token_json.get("access_token")


    # 3. 얻어낸 access token 을 이용해서 프로필 정보를 반환하는 API 를 호출하고,
    #    유저의 고유 식별 번호를 얻어낸다.
    profile_request = requests.get("https://openapi.naver.com/v1/nid/me", headers={"Authorization" : f"Bearer {access_token}"},)
    profile_data = profile_request.json()

    # 4. 얻어낸 user id 와 name 을 DB 에 저장한다.
    user_id = profile_data['response']['id']
    user_name = profile_data['response']['name']

    mydb.reconnect()
    cursor = mydb.cursor(dictionary=True)
    print(user_name)
    cursor.execute("INSERT INTO user_table VALUES(%s, %s, NULL)", (user_id, user_name))
    mydb.commit()
    cursor.close()

    # 5. 첫 페이지로 redirect 하는데 로그인 쿠키를 설정하고 보내준다.
    response = redirect('/memo')
    response.set_cookie('userId', user_id)
    return response

@app.route('/health', methods=['GET'])
def set_health():
    return '', HTTPStatus.OK


@app.route('/memo', methods=['GET'])
def get_memos():
    # 로그인이 안되어 있다면 로그인 하도록 첫 페이지로 redirect 해준다.
    userId = request.cookies.get('userId', default=None)
    if not userId:
        return redirect('/memo')

    # TODO: DB 에서 해당 userId 의 메모들을 읽어오도록 아래를 수정한다.
    result = []

    mydb.reconnect()
    cursor = mydb.cursor(buffered=True)
    query = "SELECT * FROM user_table WHERE userID = %s"
    cursor.execute(query, (userId,))
    user = cursor.fetchall()

    for i in user:
        if i[2] != None:
            t = json.dumps(json.loads(i[2]), ensure_ascii=False)
            result.append(eval(t))

    cursor.close()

    # memos라는 키 값으로 메모 목록 보내주기
    return {'memos': result}


@app.route('/memo', methods=['POST'])
def post_new_memo():
    # 로그인이 안되어 있다면 로그인 하도록 첫 페이지로 redirect 해준다.
    userId = request.cookies.get('userId', default=None)
    if not userId:
        return redirect('/memo')
    
    
    # 클라이언트로부터 JSON 을 받았어야 한다.
    if not request.is_json:
        abort(HTTPStatus.BAD_REQUEST)

    # TODO: 클라이언트로부터 받은 JSON 에서 메모 내용을 추출한 후 DB에 userId 의 메모로 추가한다.
    data = json.loads(request.data.decode("utf-8"))
    memo = data["text"]
    print(memo)

    mydb.reconnect()
    cursor = mydb.cursor(buffered=True)
    query = "SELECT * FROM user_table WHERE userID = %s"
    cursor.execute(query, (userId,))
    user = cursor.fetchone()

    # memo를 넘겨주기 위한 json 생성
    tmp = {
        "text" : memo
    }
    json_data_str = json.dumps(tmp)

    if user:
        query = "INSERT INTO user_table VALUES(%s, NULL, %s)"
        values = (userId, json_data_str,)
        cursor.execute(query, values)
        mydb.commit()
    cursor.close()
    #
    return '', HTTPStatus.OK


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080, debug=True)
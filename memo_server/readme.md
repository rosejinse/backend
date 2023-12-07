# 실행 방법

http://60212245-lb-494944562.ap-northeast-2.elb.amazonaws.com/memo

-> 위의 url을 클릭하여 접속할 수 있음

해당 url은 aws에서 설정한 로드밸런서 DNS를 이용한 것으로, 로드밸런서 내에는 대상 그룹이 있으며, 대상 그룹 내에는 "60212245-1", "60212245-2" 인스턴스가 실행되고 있다.

url에서 새로고침을 하면 두 인스턴스가 번갈아가며 보여지는 형식이다.


# `memo.py` 코드 설명
### DB 연결
--- 
먼저, `mydb = mysql.connector.connect`을 통해 aws "60212245-DB"의 Docker에서 실행 중인 mysql과 연결한다.

### 첫 페이지
---
이후, 
```
cursor = mydb.cursor(buffered=True)
query = "SELECT * FROM user_table WHERE userID = %s"
cursor.execute(query, (userId,))
```
를 통해 DB의 user_table에서 userID를 얻어오고, 이를 이용해 userId가 있는 데이터를 찾은 후, name = user[1] 과정을 통해 사용자 이름을 얻어왔다. 

이를 `index.html`에 넘겨주었다.

### 사용자 인증
---
사용자 인증을 하는 과정인 `/auth`에서는 `https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={naver_client_id}&client_secret={naver_client_secret}&code={code}&state={state}`dp requests를 하여 token을 받고, `get("access_token")`을 통해 access_token만 추출하였다.
해당 토큰을 이용하여 profile_request 과정을 통해 user 정보를 받아와 user id와 name을 db에 넘겨 저장해주었다.

저장한 뒤, `userId`를 쿠키로 설정한 뒤, 첫페이지로 redirection 해준다.

### `GET /memo`
---
첫 페이지에서 사용자 이름을 가져왔던 방법과 유사하게 json 형태의 메모를 불러온다.
메모를 불러와서 result 배열에 넣어준 뒤, `{"memos":result}`로 반환한다.

### `POST /memo`
---
클라이언트로부터 request한 memo 내용을 utf-8로 decode한 뒤 DB의 user_table에서 userID를 통해 memo를 json형태로 넘겨 저장한다.


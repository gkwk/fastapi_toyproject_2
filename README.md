# 프로젝트 목표
- 사용자가 이용할 수 있는 게시판 기능, 대화 기능, AI 모델 사용 기능을 제공할 수 있는 FastAPI 백엔드 서버를 구축한다.
- 구현된 기능의 정상 작동을 확인할 수 있는 Test코드 작성을 시도한다.
# 사용 Tools
- FastAPI
# 구현 목표
- 사용자를 위한 회원가입, 로그인, 사용자 정보 보기, 사용자 정보 수정, 게시판 접근 권한, 비밀번호 찾기 기능을 구현한다.
- 관리자를 위한 사용자
- 게시판 기능은 임의 추가 가능한 개별 게시판, 게시글 CRUD, 게시글 내 댓글 CRUD, 댓글 갯수 표시, 조회수 표시, 추천수 표시, 파일 첨부 기능으로 구성한다.
- 대화 기능은 WebSocket을 활용하여 구성한다.
- AI 모델 사용 기능은 AI 모델의 비동기 작동 및 비동기 결과 반환 기능으로 구성된다.
- 유저 확인은 JWT 라이브러리를 사용한다.
# 구현 사항
- [ ] 사용자
    - [x] 회원가입
    - [x] 로그인
    - [x] 사용자 정보 보기
    - [x] 사용자 정보 수정
    - [x] 게시판 접근 권한 보기
    - [x] 비밀번호 초기화 기능
    - [x] JWT refresh token 기능
    - [x] JWT access token 블랙리스트
    - [x] 예외 처리
    - [x] 테스트 코드 작성
    - [ ] 코드 품질 개선
- [ ] 관리자
    - [x] API가 아닌 서버 자체적인 관리자 생성
    - [x] 사용자 리스트 보기
    - [x] 사용자 게시판 접근 권한 수정
    - [x] 사용자 차단
    - [x] 게시판 추가
    - [ ] 예외 처리
    - [x] 테스트 코드 작성
    - [ ] 코드 품질 개선
- [ ] 게시판
    - [x] 임의 추가 가능한 개별 게시판
    - [x] 게시글 CRUD
    - [x] 게시글 내 댓글 CRUD
    - [x] 댓글 갯수 표시
    - [x] 조회수 표시
    - [x] 추천수 표시
    - [x] 파일 첨부 기능
    - [ ] 예외 처리
    - [x] 테스트 코드 작성
    - [ ] 코드 품질 개선
- [ ] 대화
    - [x] WebSocket활용한 관리자와의 대화
    - [x] 대화 로그 DB 저장
    - [ ] 예외 처리
    - [x] 테스트 코드 작성
    - [ ] 코드 품질 개선
- [ ] AI 모델 사용
    - [x] 비동기 작동
    - [x] 비동기 결과 반환 및 저장
    - [x] 예외 처리
    - [x] 테스트 코드 작성
    - [ ] 코드 품질 개선
# 데이터베이스
- SQLAlchemy를 사용한다.
- 개발 진행중에는 sqlite를 사용하고, 클라우드 배포시 MySQL 등으로 변경하여 프로젝트를 마무리한다.
# 데이터베이스 테이블 구조
- User
    - id : int (pk)
    - Posts: List["Post"] (1 to N)
    - Comments: List["Comment"] (1 to N)
    - ChatSessions: List["ChatSession"] (N to M)
    - boards : List["Board"] (N to M)
    - Chat: List["Chat"] (1 to N)
    - AIlogs: List["AIlog"] (1 to N)
    - name : str (unique, Not null, length=64)
    - email : str (unique, Not null, length=256)
    - password : str (hash, Not null)
    - password_salt : str (Not null)
    - join_date : datetime (Not null)
    - is_superuser : boolean (Not null, default = False)
    - is_banned : boolean (Not null, defalut = False)
    - is_active : boolean (Not null, defalut = True)
- Board
    - id : int (pk)
    - name : str (unique, Not null, length=128)
    - users : List["User"] (N to M)
    - information : str (Not null, length=512)
    - is_visible : boolean (Not null, defalut = False)
    - is_available : boolean (Not null, defalut = False)
    - permission_verified_user_id_range : int (defalut = 0)
- Post
    - id : int (pk)
    - user_id : int (user.id) (fk)
    - user : User (1 to N)
    - comments : List["Comment"] (1 to N)
    - name : str (unique, Not null, length=64)
    - content : str (Not null, length=1024)
    - create_date : datetime (Not null, default=datetime.now())
    - update_date : datetime (onupdate=datetime.now)
    - number_of_view : int (Not null, defalut = 0)
    - number_of_comment : int (Not null, defalut = 0)
    - number_of_like : int (Not null, defalut = 0)
    - is_file_attached : boolean (Not null, defalut = False)
    - attached_files : List["PostFile"] (1 to N)
    - is_visible : boolean (Not null, defalut = True)
- Comment
    - id : int (pk)
    - user_id : int (user.id) (fk)
    - user : User (1 to N)
    - post_id : int (post.id) (fk)
    - post : Post (1 to N)
    - content : str (Not null, length=256)
    - create_date : datetime (Not null, default=datetime.now())
    - update_date : datetime (onupdate=datetime.now)
    - is_file_attached : boolean (Not null, defalut = False)
    - attached_files : List["PostFile"] (1 to N)
    - is_visible : boolean (Not null, defalut = True)
- ChatSession
    - id : int (pk)
    - users : List["User"] (N to M)
    - chats : List["Chat"] (1 to N)
    - name : str (Not null, length=256)
    - information : str (Not null, length=256)
    - create_date : datetime (Not null, default=datetime.now())
    - update_date : datetime (onupdate=datetime.now)
    - is_visible : boolean (Not null, defalut = True)
    - is_closed : boolean (Not null, defalut = False)
- Chat
    - id : int (pk)
    - user_id : int (user.id) (fk)
    - user : User (1 to N)
    - chat_session_id : int (chat_session.id) (fk)
    - chat_session : ChatSession (1 to N)
    - content : str (Not null, length=256)
    - create_date : datetime (Not null, default=datetime.now())
    - update_date : datetime (onupdate=datetime.now)
    - is_visible : boolean (Not null, defalut = True)
- AI
    - id : int (pk)
    - ai_logs : List["AIlog"] (1 to N)
    - name : str (unique, Not null, length=64)
    - description : str (Not null, length=256)
    - create_date : datetime (Not null, default=datetime.now())
    - update_date : datetime (onupdate=datetime.now)
    - finish_date : datetime
    - is_visible : boolean (Not null, defalut = False)
    - is_available : boolean (Not null, defalut = False)
    - celery_task_id : str (Not null, length=64)
- AIlog
    - id : int (pk)
    - user_id : int (user.id) (fk)
    - user : User (1 to N)
    - ai_id : int (AI.id) (fk)
    - ai : AI (1 to N)
    - description : str (Not null, length=256)
    - result : str (Not null, length=256)
    - create_date : datetime (Not null, default=datetime.now())
    - update_date : datetime (onupdate=datetime.now)
    - finish_date : datetime
    - is_finished : boolean (Not null, defalut = False)
    - celery_task_id : str (Not null, length=64)
- UserChatSessionTable
    - user_id : int (user.id) (pk, fk)
    - chat_session_id : int (chat_session.id) (pk, fk)
    - create_date : datetime (Not null, default=datetime.now())
- UserPermissionTable
    - user_id : int (user.id) (pk, fk)
    - board_id : int (board.id) (pk, fk)
    - create_date : datetime (Not null, default=datetime.now())
- JWTAccessTokenBlackList
    - user_id : int (pk, autoincrement=False)
    - access_token : str (pk)
    - create_date : datetime (Not null, default=datetime.now(), onupdate=datetime.now)
    - expired_date : datetime
- JWTRefreshTokenList
    - user_id : int (pk, autoincrement=False)
    - refresh_token : str (Not null)
    - access_token : str
    - create_date : datetime (Not null, default=datetime.now(), onupdate=datetime.now)
    - expired_date : datetime
- PostFile
    - post_id : int (post.id) (pk, fk)
    - post : Post (1 to N)
    - board_id : int (board.id) (pk, fk)
    - file_uuid_name : str (pk)
    - file_original_name : str
    - file_path : str
    - create_date : datetime (Not null, default=datetime.now())
- CommentFile
    - comment_id : int (comment.id) (pk, fk)
    - comment : Comment (1 to N)
    - post_id : int (post.id) (pk, fk)
    - file_uuid_name : str (pk)
    - file_original_name : str
    - file_path : str
    - create_date : datetime (Not null, default=datetime.now())

# AI_test.csv
```math
y = 4x_0 + 5x_1 + 2x_2 + 7x_3 + 0.1x_4 + 15x_5 + 0.05x_6+ x_7
```

# 실행방법(자동)
- .env 파일 작성
- 터미널에서 아래의 명령어 입력
```bash
sudo bash project_init.sh
```

# 실행방법(수동)
- .env 파일 작성
- 터미널에서 아래의 명령어 입력
```bash
alembic init migrations
```
- `./alembic.ini` 에서 `sqlalchemy.url`를 아래와 같이 변경
```ini
sqlalchemy.url = sqlite:///./test.sqlite
```
- `./migrations/env.py` 에서 아래의 내용 추가
```python
import models
```
- `./migrations/env.py` 에서 `target_metadata`를 아래와 같이 변경
```python
target_metadata = models.base.metadata
```
- 터미널에서 아래의 명령어 입력
```bash
alembic revision --autogenerate
alembic upgrade head
```
- 각각의 터미널에서 아래의 명령어들을 입력
```bash
python main.py
celery -A celery_app worker -l info --pool=solo
```

# SQLite 사용시 추가사항
- alembic init 후 migration 내 env.py 에서 다음과 같이 수정사항 반영
- SQLite의 ALTER 미지원 문제를 해결하여 DB Column을 변경할 수 있게 해준다.
```python
with connectable.connect() as connection:
    context.configure(
        connection=connection, target_metadata=target_metadata,
        render_as_batch=True #추가사항
    )
```

# 개선을 위한 임시 목표 (개선 후 삭제)
- admin, board, chat 기능 예외 처리 코드 추가
- post 의 조회수나 추천수 등을 자동으로 증가시키는 함수 추가
- 조회수같이 자주 변하지만 사용자 입장에서 실시간 확인 필요성이 떨어지는 부분의 db 수정 쿼리가 몰아서 반영 될 수 있도록 구축
- csrf 토큰 등의 보안 미들웨어 추가
- 쿠버네티스를 통해 스테이징 서버 구축시 완전 자동으로 테스트가 진행 될 수 있도록 하기
- 예외 메세지나 URL 경로 등은 하나의 파일에 정리하는 등의 조치로 중복 코드 정리
    - 테스트 코드의 중복 코드(로그인 등) 정리
- test app 생성
- test 코드를 test app에서 동작하도록 변경
- test app에서 create시 id 반환하게 하고 이를 통해 test 코드 개선
- test app과 production app 구분되도록 만들고 db도 분리

# pytest 사용법 예시
```bash
pytest
pytest -s
pytest path
pytest path/file_name.py
pytest path/file_name.py::class::method
```

# 도커 사용법 (AWS EC2 - ubuntu 22.04 기준)
- VPC 구성
- 서브넷 구성
- 인터넷 게이트웨이 구성
- EC2 인스턴스 구성
- Docker 설치
```bash
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install docker-ce
```
- Docker 버전 확인 (설치 확인):
```bash
docker version
```
- Docker 서비스 시작 및 활성화:
```bash
sudo systemctl start docker
sudo systemctl enable docker
```
-  Docker Compose 설치:
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.1.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
- Docker Compose 버전 확인 (설치 확인):
```bash
docker-compose --version
```
- Docker image 빌드
```bash
docker build -t image-name:tag
```
- Docker image를 로컬 저장
```bash
docker save -o image-name.tar image-name:tag
```
- Docker image와 docker-compose.yml을 EC2 인스턴스에 전송
- Docker image를 인스턴스의 도커에 등록
```bash
docker load -i image-name.tar
```
- docker-compose.yml에 기재된 환경 추가 설정
- docker-compose 프로젝트 실행
```bash
docker-compose up -d
```
- docker-compose 프로젝트 확인
```bash
docker-compose ps
```
- docker-compose 프로젝트 종료
```bash
docker-compose down
```
- docker-compose의 컨테이너 터미널 사용
```bash
docker exec -it container-id/name /bin/bash
```

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
- AI 모델 사용 기능은 PyTorch 모델의 비동기 작동 및 비동기 결과 반환 기능으로 구성된다.
- 유저 확인은 JWT 라이브러리를 사용한다.
# 구현 사항
- [ ] 사용자
    - [x] 회원가입
    - [x] 로그인
    - [x] 사용자 정보 보기
    - [x] 사용자 정보 수정
    - [x] 게시판 접근 권한 보기
    - [x] 비밀번호 초기화 기능
- [ ] 관리자
    - [x] API가 아닌 서버 자체적인 관리자 생성
    - [x] 사용자 리스트 보기
    - [x] 사용자 게시판 접근 권한 수정
    - [x] 사용자 차단
    - [x] 게시판 추가
- [ ] 게시판
    - [x] 임의 추가 가능한 개별 게시판
    - [x] 게시글 CRUD
    - [x] 게시글 내 댓글 CRUD
    - [ ] 댓글 갯수 표시
    - [ ] 조회수 표시
    - [ ] 추천수 표시
    - [ ] 파일 첨부 기능
- [ ] 대화
    - [ ] WebSocket활용한 관리자와의 대화
- [ ] AI 모델 사용
    - [ ] 비동기 작동
    - [ ] 비동기 결과 반환 및 저장
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
- Board
    - id : int (pk)
    - name : str (unique, Not null, length=128)
    - users : List["User"] (N to M)
    - information : str (Not null, length=512)
    - is_visible : boolean (Not null, defalut = True)
- Post
    - id : int (pk)
    - user_id : int (user.id) (fk)
    - user : User (1 to N)
    - comments : List["Comment"] (1 to N)
    - name : str (unique, Not null, length=64)
    - content : str (Not null, length=1024)
    - create_date : datetime (Not null, default=datetime.now())
    - update_date : datetime (Not null)
    - number_of_view : int (Not null, defalut = 0)
    - number_of_comment : int (Not null, defalut = 0)
    - number_of_like : int (Not null, defalut = 0)
    - is_file_attached : boolean (Not null, defalut = False)
    - is_visible : boolean (Not null, defalut = True)
- Comment
    - id : int (pk)
    - user_id : int (user.id) (fk)
    - user : User (1 to N)
    - post_id : int (post.id) (fk)
    - post : Post (1 to N)
    - content : str (Not null, length=256)
    - create_date : datetime (Not null, default=datetime.now())
    - update_date : datetime (Not null)
    - is_file_attached : boolean (Not null, defalut = False)
    - is_visible : boolean (Not null, defalut = True)
- ChatSession
    - id : int (pk)
    - users : List["User"] (N to M)
    - chats : List["Chat"] (1 to N)
    - name : str (Not null, length=256)
    - create_date : datetime (Not null, default=datetime.now())
    - update_date : datetime (Not null)
- Chat
    - id : int (pk)
    - user_id : int (user.id) (fk)
    - user : User (1 to N)
    - chat_session_id : int (chat_session.id) (fk)
    - chat_session : ChatSession (1 to N)
    - content : str (Not null, length=256)
    - create_date : datetime (Not null, default=datetime.now())
    - is_visible : boolean (Not null, defalut = True)
- AI
    - id : int (pk)
    - ai_logs : List["AIlog"] (1 to N)
    - name : str (unique, Not null, length=64)
    - information : str (Not null, length=256)
    - is_visible : boolean (Not null, defalut = True)
- AIlog
    - id : int (pk)
    - user_id : int (user.id) (fk)
    - user : User (1 to N)
    - ai_id : int (AI.id) (fk)
    - ai : AI (1 to N)
    - content : str (Not null, length=256)
    - create_date : datetime (Not null, default=datetime.now())
    - finish_date : datetime (Not null)
    - is_finished : boolean (Not null, defalut = False)

# 실행방법
- 터미널에서 아래의 명령어 입력
```bash
alembic init migrations
```
- `./alembic.ini` 에서 `sqlalchemy.url`를 아래와 같이 변경
```
sqlalchemy.url = sqlite:///./test.sqlite
```
- `./migrations/env.py` 에서 아래의 내용 추가
```
import models
```
- `./migrations/env.py` 에서 `target_metadata`를 아래와 같이 변경
```
target_metadata = models.base.metadata
```
- 터미널에서 아래의 명령어 입력
```bash
alembic revision --autogenerate
alembic upgrade head
```
- 터미널에서 아래의 명령어 입력
```bash
uvicorn main:app --reload
```
from pytest import MonkeyPatch

from fastapi.testclient import TestClient

from main import app
from domain.admin.admin_crud import create_admin_with_terminal
from models import User, Board, Post, Comment
from database import session_local
from auth import validate_and_decode_user_access_token

client = TestClient(app)

data_base = session_local()

data_base.query(User).delete()
data_base.query(Board).delete()
data_base.query(Post).delete()
data_base.query(Comment).delete()
data_base.commit()


TEST_ADMIN_ID = "admin"
TEST_ADMIN_EMAIL = "admin@test.com"
TEST_ADMIN_PASSWORD1 = "12345678"
TEST_ADMIN_PASSWORD2 = "12345678"

TEST_USER_ID = "user"
TEST_USER_EMAIL = "user@test.com"
TEST_USER_PASSWORD1 = "12345678"
TEST_USER_PASSWORD2 = "12345678"
TEST_USER_IS_PERMMITED_UPDATE = True
TEST_USER_IS_BANNED_UPDATE = True

TEST_BOARD_NAME = "board"
TEST_BOARD_INFORMATION = "board_create_test"
TEST_BOARD_IS_VISIBLE = True

TEST_POST_NAME = "post"
TEST_POST_CONTENT = "post_content"
TEST_POST_IS_FILE_ATTACHED = False
TEST_POST_IS_VISIBLE = True
TEST_POST_NAME_UPDATE = "post_update"
TEST_POST_CONTENT_UPDATE = "post_content_update"

TEST_COMMENT_CONTENT = "comment_content"
TEST_COMMENT_IS_FILE_ATTACHED = False
TEST_COMMENT_IS_VISIBLE = True
TEST_COMMENT_CONTENT_UPDATE = "comment_content_update"


class TestPost:
    def test_data_base_init(self):
        data_base = session_local()
        data_base.query(Comment).delete()
        data_base.query(Post).delete()
        data_base.query(Board).delete()
        data_base.query(User).delete()
        data_base.commit()
        data_base.close()

    def test_create_admin(self):
        input_iter = iter([TEST_ADMIN_ID, TEST_ADMIN_EMAIL]).__next__
        getpass_iter = iter([TEST_ADMIN_PASSWORD1, TEST_ADMIN_PASSWORD2]).__next__

        monkeypatch = MonkeyPatch()
        monkeypatch.setattr("builtins.input", input_iter)
        monkeypatch.setattr("getpass.getpass", getpass_iter)

        create_admin_with_terminal(data_base=None)

    def test_create_user(self):
        data_base = session_local()

        response_test = client.post(
            "/api/v1/user/create_user",
            json={
                "name": TEST_USER_ID,
                "password1": TEST_USER_PASSWORD1,
                "password2": TEST_USER_PASSWORD2,
                "email": TEST_USER_EMAIL,
            },
        )

        assert response_test.status_code == 201
        assert response_test.json() == {"result": "success"}

        user = (
            data_base.query(User)
            .filter_by(name=TEST_USER_ID, email=TEST_USER_EMAIL)
            .first()
        )
        assert user.name == TEST_USER_ID
        assert user.email == TEST_USER_EMAIL
        assert user.password != None
        assert user.password_salt != None
        assert user.join_date != None
        assert user.is_superuser == False
        assert user.is_banned == False

        data_base.close()

    def test_create_board(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        response_test = client.post(
            "/api/v1/admin/create_board",
            json={
                "name": TEST_BOARD_NAME,
                "information": TEST_BOARD_INFORMATION,
                "is_visible": TEST_BOARD_IS_VISIBLE,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 201
        assert response_test.json() == {"result": "success"}

        board = (
            data_base.query(Board)
            .filter_by(name=TEST_BOARD_NAME, information=TEST_BOARD_INFORMATION)
            .first()
        )

        assert board.name == TEST_BOARD_NAME
        assert board.information == TEST_BOARD_INFORMATION
        assert board.is_visible == TEST_BOARD_IS_VISIBLE

        data_base.close()

    def test_create_post(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        board = (
            data_base.query(Board)
            .filter_by(name=TEST_BOARD_NAME, information=TEST_BOARD_INFORMATION)
            .first()
        )
        user = (
            data_base.query(User)
            .filter_by(name=TEST_ADMIN_ID, email=TEST_ADMIN_EMAIL)
            .first()
        )

        response_test = client.post(
            "/api/v1/board/create_post",
            json={
                "name": TEST_POST_NAME,
                "content": TEST_POST_CONTENT,
                "board_id": board.id,
                "is_file_attached": TEST_POST_IS_FILE_ATTACHED,
                "is_visible": TEST_POST_IS_VISIBLE,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 201
        assert response_test.json() == {"result": "success"}

        post = data_base.query(Post).filter_by(name=TEST_POST_NAME).first()

        assert post.user_id == user.id
        assert post.board_id == board.id
        assert post.name == TEST_POST_NAME
        assert post.content == TEST_POST_CONTENT
        assert post.create_date != None
        assert post.update_date == None
        assert post.number_of_comment == 0
        assert post.number_of_view == 0
        assert post.number_of_like == 0
        assert post.is_file_attached == TEST_POST_IS_FILE_ATTACHED
        assert post.is_visible == TEST_POST_IS_VISIBLE
        data_base.close()

    def test_get_post(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        board = (
            data_base.query(Board)
            .filter_by(name=TEST_BOARD_NAME, information=TEST_BOARD_INFORMATION)
            .first()
        )
        post = data_base.query(Post).filter_by(name=TEST_POST_NAME).first()

        response_test = client.get(
            "/api/v1/board/get_post",
            params={
                "id": post.id,
                "board_id": board.id,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        assert response_test_json.get("id") == post.id
        assert response_test_json.get("name") == post.name
        assert response_test_json.get("content") == post.content
        assert response_test_json.get("board_id") == post.board_id
        assert response_test_json.get("create_date") != None
        assert response_test_json.get("number_of_view") == post.number_of_view
        assert response_test_json.get("number_of_comment") == post.number_of_comment
        assert response_test_json.get("number_of_like") == post.number_of_like
        assert response_test_json.get("is_file_attached") == post.is_file_attached
        assert response_test_json.get("is_visible") == post.is_visible
        data_base.close()

    def test_get_posts(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        board = (
            data_base.query(Board)
            .filter_by(name=TEST_BOARD_NAME, information=TEST_BOARD_INFORMATION)
            .first()
        )

        response_test = client.get(
            "/api/v1/board/get_posts",
            params={
                "board_id": board.id,
                "skip": 0,
                "limit": 20,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        assert response_test_json.get("total") >= 0

        for post in response_test_json.get("posts"):
            post: dict

            assert post.get("id") > 0
            assert post.get("name") != None
            assert post.get("content") != None
            assert post.get("board_id") == board.id
            assert post.get("create_date") != None
            assert post.get("number_of_view") >= 0
            assert post.get("number_of_comment") >= 0
            assert post.get("number_of_like") >= 0
            assert post.get("is_file_attached") != None
            assert post.get("is_visible") != None

        data_base.close()

    def test_update_post(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        board = (
            data_base.query(Board)
            .filter_by(name=TEST_BOARD_NAME, information=TEST_BOARD_INFORMATION)
            .first()
        )
        post = data_base.query(Post).filter_by(name=TEST_POST_NAME).first()

        response_test = client.put(
            "/api/v1/board/update_post",
            json={
                "id": post.id,
                "name": TEST_POST_NAME_UPDATE,
                "content": TEST_POST_CONTENT_UPDATE,
                "board_id": board.id,
                "is_file_attached": TEST_POST_IS_FILE_ATTACHED,
                "is_visible": TEST_POST_IS_VISIBLE,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        data_base.commit()

        assert response_test.status_code == 204

        assert post.name == TEST_POST_NAME_UPDATE
        assert post.content == TEST_POST_CONTENT_UPDATE
        data_base.close()

    def test_delete_post(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        board = (
            data_base.query(Board)
            .filter_by(name=TEST_BOARD_NAME, information=TEST_BOARD_INFORMATION)
            .first()
        )
        post = data_base.query(Post).filter_by(name=TEST_POST_NAME_UPDATE).first()

        response_test = client.delete(
            "/api/v1/board/delete_post",
            params={
                "id": post.id,
                "board_id": board.id,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        data_base.commit()

        assert response_test.status_code == 204

        post = data_base.query(Post).filter_by(name=TEST_POST_NAME_UPDATE).first()

        assert post == None

        data_base.close()


class TestComment:
    def test_data_base_init(self):
        data_base = session_local()
        data_base.query(Comment).delete()
        data_base.query(Post).delete()
        data_base.query(Board).delete()
        data_base.query(User).delete()
        data_base.commit()
        data_base.close()

    def test_create_admin(self):
        input_iter = iter([TEST_ADMIN_ID, TEST_ADMIN_EMAIL]).__next__
        getpass_iter = iter([TEST_ADMIN_PASSWORD1, TEST_ADMIN_PASSWORD2]).__next__

        monkeypatch = MonkeyPatch()
        monkeypatch.setattr("builtins.input", input_iter)
        monkeypatch.setattr("getpass.getpass", getpass_iter)

        create_admin_with_terminal(data_base=None)

    def test_create_user(self):
        data_base = session_local()

        response_test = client.post(
            "/api/v1/user/create_user",
            json={
                "name": TEST_USER_ID,
                "password1": TEST_USER_PASSWORD1,
                "password2": TEST_USER_PASSWORD2,
                "email": TEST_USER_EMAIL,
            },
        )

        assert response_test.status_code == 201
        assert response_test.json() == {"result": "success"}

        user = (
            data_base.query(User)
            .filter_by(name=TEST_USER_ID, email=TEST_USER_EMAIL)
            .first()
        )
        assert user.name == TEST_USER_ID
        assert user.email == TEST_USER_EMAIL
        assert user.password != None
        assert user.password_salt != None
        assert user.join_date != None
        assert user.is_superuser == False
        assert user.is_banned == False

        data_base.close()

    def test_create_board(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        response_test = client.post(
            "/api/v1/admin/create_board",
            json={
                "name": TEST_BOARD_NAME,
                "information": TEST_BOARD_INFORMATION,
                "is_visible": TEST_BOARD_IS_VISIBLE,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 201
        assert response_test.json() == {"result": "success"}

        board = (
            data_base.query(Board)
            .filter_by(name=TEST_BOARD_NAME, information=TEST_BOARD_INFORMATION)
            .first()
        )

        assert board.name == TEST_BOARD_NAME
        assert board.information == TEST_BOARD_INFORMATION
        assert board.is_visible == TEST_BOARD_IS_VISIBLE

        data_base.close()

    def test_create_post(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        board = (
            data_base.query(Board)
            .filter_by(name=TEST_BOARD_NAME, information=TEST_BOARD_INFORMATION)
            .first()
        )
        user = (
            data_base.query(User)
            .filter_by(name=TEST_ADMIN_ID, email=TEST_ADMIN_EMAIL)
            .first()
        )

        response_test = client.post(
            "/api/v1/board/create_post",
            json={
                "name": TEST_POST_NAME,
                "content": TEST_POST_CONTENT,
                "board_id": board.id,
                "is_file_attached": TEST_POST_IS_FILE_ATTACHED,
                "is_visible": TEST_POST_IS_VISIBLE,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 201
        assert response_test.json() == {"result": "success"}

        post = data_base.query(Post).filter_by(name=TEST_POST_NAME).first()

        assert post.user_id == user.id
        assert post.board_id == board.id
        assert post.name == TEST_POST_NAME
        assert post.content == TEST_POST_CONTENT
        assert post.create_date != None
        assert post.update_date == None
        assert post.number_of_comment == 0
        assert post.number_of_view == 0
        assert post.number_of_like == 0
        assert post.is_file_attached == TEST_POST_IS_FILE_ATTACHED
        assert post.is_visible == TEST_POST_IS_VISIBLE
        data_base.close()

    def test_create_comment(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        user = (
            data_base.query(User)
            .filter_by(name=TEST_ADMIN_ID, email=TEST_ADMIN_EMAIL)
            .first()
        )
        post = data_base.query(Post).filter_by(name=TEST_POST_NAME).first()

        response_test = client.post(
            "/api/v1/board/create_comment",
            json={
                "content": TEST_COMMENT_CONTENT,
                "post_id": post.id,
                "is_file_attached": TEST_COMMENT_IS_FILE_ATTACHED,
                "is_visible": TEST_COMMENT_IS_VISIBLE,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 201
        assert response_test.json() == {"result": "success"}

        comment = (
            data_base.query(Comment)
            .filter_by(post_id=post.id, content=TEST_COMMENT_CONTENT)
            .first()
        )

        assert comment.user_id == user.id
        assert comment.post_id == post.id
        assert comment.content == TEST_COMMENT_CONTENT
        assert comment.create_date != None
        assert comment.update_date == None
        assert comment.is_file_attached == TEST_COMMENT_IS_FILE_ATTACHED
        assert comment.is_visible == TEST_COMMENT_IS_VISIBLE
        data_base.close()

    def test_get_comment(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        post = data_base.query(Post).filter_by(name=TEST_POST_NAME).first()
        comment = (
            data_base.query(Comment)
            .filter_by(post_id=post.id, content=TEST_COMMENT_CONTENT)
            .first()
        )

        response_test = client.get(
            "/api/v1/board/get_comment",
            params={
                "id": comment.id,
                "post_id": post.id,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        assert response_test_json.get("id") == comment.id
        assert response_test_json.get("content") == comment.content
        assert response_test_json.get("post_id") == comment.post_id
        assert response_test_json.get("create_date") != None
        assert response_test_json.get("update_date") == None
        assert response_test_json.get("is_file_attached") == comment.is_file_attached
        assert response_test_json.get("is_visible") == comment.is_visible
        data_base.close()

    def test_get_comments(self):
        data_base = session_local()
        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        post = data_base.query(Post).filter_by(name=TEST_POST_NAME).first()

        response_test = client.get(
            "/api/v1/board/get_comments",
            params={
                "post_id": post.id,
                "skip": 0,
                "limit": 20,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        assert response_test_json.get("total") >= 0

        for comment in response_test_json.get("comments"):
            comment: dict

            assert comment.get("id") > 0
            assert comment.get("content") != None
            assert comment.get("post_id") == post.id
            assert comment.get("create_date") != None
            assert comment.get("is_file_attached") != None
            assert comment.get("is_visible") != None
        data_base.close()

    def test_update_comment(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        post = data_base.query(Post).filter_by(name=TEST_POST_NAME).first()
        comment = (
            data_base.query(Comment)
            .filter_by(post_id=post.id, content=TEST_COMMENT_CONTENT)
            .first()
        )

        response_test = client.put(
            "/api/v1/board/update_comment",
            json={
                "id": comment.id,
                "content": TEST_COMMENT_CONTENT_UPDATE,
                "post_id": post.id,
                "is_file_attached": TEST_COMMENT_IS_FILE_ATTACHED,
                "is_visible": TEST_COMMENT_IS_VISIBLE,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        data_base.commit()

        assert response_test.status_code == 204

        assert comment.content == TEST_COMMENT_CONTENT_UPDATE
        assert comment.update_date != None
        data_base.close()

    def test_delete_comment(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        post = data_base.query(Post).filter_by(name=TEST_POST_NAME).first()
        comment = (
            data_base.query(Comment)
            .filter_by(post_id=post.id, content=TEST_COMMENT_CONTENT_UPDATE)
            .first()
        )

        response_test = client.delete(
            "/api/v1/board/delete_comment",
            params={
                "id": comment.id,
                "post_id": post.id,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        data_base.commit()

        assert response_test.status_code == 204

        comment = (
            data_base.query(Comment)
            .filter_by(post_id=post.id, content=TEST_COMMENT_CONTENT_UPDATE)
            .first()
        )

        assert comment == None
        
        data_base.close()

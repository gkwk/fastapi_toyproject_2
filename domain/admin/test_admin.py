from pytest import MonkeyPatch

from fastapi.testclient import TestClient

from main import app
from domain.admin.admin_crud import create_admin_with_terminal
from models import User, Board, UserPermissionTable
from database import session_local

client = TestClient(app)


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


class TestAdmin:
    def test_data_base_init(self):
        data_base = session_local()
        data_base.query(Board).delete()
        data_base.query(UserPermissionTable).delete()
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

    def test_get_users(self):
        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        response_test = client.get(
            "/api/v1/admin/get_users",
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        for user in response_test_json.get("users"):
            user: dict

            assert user.get("name") != None
            assert user.get("email") != None
            assert user.get("join_date") != None
            assert user.get("boards") != None
            assert user.get("posts") != None

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

    def test_update_user_board_permission(self):
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
            .filter_by(name=TEST_USER_ID, email=TEST_USER_EMAIL)
            .first()
        )
        board = (
            data_base.query(Board)
            .filter_by(name=TEST_BOARD_NAME, information=TEST_BOARD_INFORMATION)
            .first()
        )

        response_test = client.put(
            "/api/v1/admin/update_user_board_permission",
            json={
                "user_id": user.id,
                "board_id": board.id,
                "is_permitted": TEST_USER_IS_PERMMITED_UPDATE,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        data_base.commit()

        assert response_test.status_code == 204

        user = (
            data_base.query(User)
            .filter_by(name=TEST_USER_ID, email=TEST_USER_EMAIL)
            .first()
        )

        assert board.id in [board.id for board in user.boards]

        data_base.close()

    def test_update_user_is_banned(self):
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
            .filter_by(name=TEST_USER_ID, email=TEST_USER_EMAIL)
            .first()
        )

        response_test = client.put(
            "/api/v1/admin/update_user_is_banned",
            json={
                "user_id": user.id,
                "is_banned": TEST_USER_IS_BANNED_UPDATE,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        data_base.commit()

        assert response_test.status_code == 204

        user = (
            data_base.query(User)
            .filter_by(name=TEST_USER_ID, email=TEST_USER_EMAIL)
            .first()
        )

        assert user.is_banned == TEST_USER_IS_BANNED_UPDATE

        data_base.close()

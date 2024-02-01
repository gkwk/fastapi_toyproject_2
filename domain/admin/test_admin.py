from pytest import MonkeyPatch
import time

from fastapi.testclient import TestClient

from celery.result import AsyncResult

from main import app
from domain.admin.admin_crud import create_admin_with_terminal
from models import User, Board, UserPermissionTable
from database import session_local, engine
from auth import validate_and_decode_user_access_token

client = TestClient(app)

data_base = session_local()

data_base.query(User).delete()
data_base.commit()

data_base.query(Board).delete()
data_base.commit()

data_base.query(UserPermissionTable).delete()
data_base.commit()


TEST_ADMIN_ID = "admin_admin"
TEST_ADMIN_EMAIL = "admin_admin@test.com"
TEST_ADMIN_PASSWORD1 = "12345678"
TEST_ADMIN_PASSWORD2 = "12345678"

TEST_USER_ID = "user_admin"
TEST_USER_EMAIL = "user_admin@test.com"
TEST_USER_PASSWORD1 = "12345678"
TEST_USER_PASSWORD2 = "12345678"
TEST_USER_IS_PERMMITED_UPDATE = True
TEST_USER_IS_BANNED_UPDATE = True

TEST_BOARD_NAME = "board_admin"
TEST_BOARD_INFORMATION = "board_create_test"
TEST_BOARD_IS_VISIBLE = True


def test_create_admin():
    input_iter = iter([TEST_ADMIN_ID, TEST_ADMIN_EMAIL]).__next__
    getpass_iter = iter([TEST_ADMIN_PASSWORD1, TEST_ADMIN_PASSWORD2]).__next__

    monkeypatch = MonkeyPatch()
    monkeypatch.setattr("builtins.input", input_iter)
    monkeypatch.setattr("getpass.getpass", getpass_iter)

    create_admin_with_terminal()


def test_create_user():
    response_test = client.post(
        "/api/v1/user/create",
        json={
            "name": TEST_USER_ID,
            "password1": TEST_USER_PASSWORD1,
            "password2": TEST_USER_PASSWORD2,
            "email": TEST_USER_EMAIL,
        },
    )

    assert response_test.status_code == 204

    user = data_base.query(User).order_by(User.id.desc()).first()

    assert user.name == TEST_USER_ID
    assert user.email == TEST_USER_EMAIL
    assert user.password != None
    assert user.password_salt != None
    assert user.join_date != None
    assert user.is_superuser == False
    assert user.is_banned == False


def test_get_users():
    response_login = client.post(
        "/api/v1/user/login",
        data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert response_login.status_code == 200
    response_login_json: dict = response_login.json()
    assert response_login_json.get("access_token")
    assert response_login_json.get("token_type")

    response_test = client.get(
        "/api/v1/admin/get_users",
        headers={"Authorization": f"Bearer {response_login_json.get('access_token')}"},
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


def test_create_board():
    response_login = client.post(
        "/api/v1/user/login",
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
        headers={"Authorization": f"Bearer {response_login_json.get('access_token')}"},
    )

    assert response_test.status_code == 204

    board = data_base.query(Board).first()

    assert board.name == TEST_BOARD_NAME
    assert board.information == TEST_BOARD_INFORMATION
    assert board.is_visible == TEST_BOARD_IS_VISIBLE


def test_update_user_board_permission():
    response_login = client.post(
        "/api/v1/user/login",
        data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert response_login.status_code == 200
    response_login_json: dict = response_login.json()
    assert response_login_json.get("access_token")
    assert response_login_json.get("token_type")

    user = data_base.query(User).filter_by(name=TEST_USER_ID).first()
    board = data_base.query(Board).first()

    response_test = client.put(
        "/api/v1/admin/update_user_board_permission",
        json={
            "user_id": user.id,
            "board_id": board.id,
            "is_permitted": TEST_USER_IS_PERMMITED_UPDATE,
        },
        headers={"Authorization": f"Bearer {response_login_json.get('access_token')}"},
    )

    data_base.commit()

    assert response_test.status_code == 204

    user = data_base.query(User).filter_by(name=TEST_USER_ID).first()

    assert board.id in [board.id for board in user.boards]


def test_update_user_is_banned():
    response_login = client.post(
        "/api/v1/user/login",
        data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert response_login.status_code == 200
    response_login_json: dict = response_login.json()
    assert response_login_json.get("access_token")
    assert response_login_json.get("token_type")

    user = data_base.query(User).filter_by(name=TEST_USER_ID).first()
    board = data_base.query(Board).first()

    response_test = client.put(
        "/api/v1/admin/update_user_is_banned",
        json={
            "user_id": user.id,
            "is_banned": TEST_USER_IS_BANNED_UPDATE,
        },
        headers={"Authorization": f"Bearer {response_login_json.get('access_token')}"},
    )

    data_base.commit()

    assert response_test.status_code == 204

    user = data_base.query(User).filter_by(name=TEST_USER_ID).first()

    assert user.is_banned == TEST_USER_IS_BANNED_UPDATE


engine.dispose()

from pytest import MonkeyPatch
import time

from fastapi.testclient import TestClient

from celery.result import AsyncResult

from main import app
from domain.admin.admin_crud import create_admin_with_terminal
from models import User
from database import session_local, engine
from auth import validate_and_decode_user_access_token

client = TestClient(app)

data_base = session_local()
data_base.query(User).delete()
data_base.commit()


TEST_ADMIN_ID = "admin_user"
TEST_ADMIN_EMAIL = "admin_user@test.com"
TEST_ADMIN_PASSWORD1 = "12345678"
TEST_ADMIN_PASSWORD2 = "12345678"

TEST_USER_ID = "user_user"
TEST_USER_EMAIL = "user_user@test.com"
TEST_USER_PASSWORD1 = "12345678"
TEST_USER_PASSWORD2 = "12345678"

TEST_USER_EMAIL_UPDATE = "user_user_update@test.com"
TEST_USER_PASSWORD1_UPDATE = "123456789"
TEST_USER_PASSWORD2_UPDATE = "123456789"


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


def test_login_user():
    response_login = client.post(
        "/api/v1/user/login",
        data={"username": TEST_USER_ID, "password": TEST_USER_PASSWORD1},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert response_login.status_code == 200
    response_login_json: dict = response_login.json()
    assert response_login_json.get("access_token")
    assert response_login_json.get("token_type") == "bearer"
    assert response_login_json.get("is_admin") == None


def test_get_user_detail():
    response_login = client.post(
        "/api/v1/user/login",
        data={"username": TEST_USER_ID, "password": TEST_USER_PASSWORD1},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert response_login.status_code == 200
    response_login_json: dict = response_login.json()
    assert response_login_json.get("access_token")
    assert response_login_json.get("token_type")

    user_id = validate_and_decode_user_access_token(
        response_login_json.get("access_token")
    ).get("user_id")

    response_test = client.get(
        "/api/v1/user/detail",
        headers={"Authorization": f"Bearer {response_login_json.get('access_token')}"},
    )

    data_base.commit()

    assert response_test.status_code == 200

    response_test_json: dict = response_test.json()

    assert response_test_json.get("name") == TEST_USER_ID
    assert response_test_json.get("email") == TEST_USER_EMAIL
    assert response_test_json.get("join_date") != None
    assert response_test_json.get("boards") != None
    assert response_test_json.get("posts") != None


def test_update_user_detail():
    response_login = client.post(
        "/api/v1/user/login",
        data={"username": TEST_USER_ID, "password": TEST_USER_PASSWORD1},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert response_login.status_code == 200
    response_login_json: dict = response_login.json()
    assert response_login_json.get("access_token")
    assert response_login_json.get("token_type")

    user_id = validate_and_decode_user_access_token(
        response_login_json.get("access_token")
    ).get("user_id")

    response_test = client.put(
        "/api/v1/user/update_detail",
        json={
            "email": TEST_USER_EMAIL_UPDATE,
        },
        headers={"Authorization": f"Bearer {response_login_json.get('access_token')}"},
    )

    data_base.commit()

    assert response_test.status_code == 204

    user = data_base.query(User).filter_by(id=user_id).first()

    assert user.name == TEST_USER_ID
    assert user.email == TEST_USER_EMAIL_UPDATE
    assert user.password != None
    assert user.password_salt != None
    assert user.join_date != None
    assert user.is_superuser == False
    assert user.is_banned == False


def test_update_user_password():
    response_login = client.post(
        "/api/v1/user/login",
        data={"username": TEST_USER_ID, "password": TEST_USER_PASSWORD1},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert response_login.status_code == 200
    response_login_json: dict = response_login.json()
    assert response_login_json.get("access_token")
    assert response_login_json.get("token_type")

    user_id = validate_and_decode_user_access_token(
        response_login_json.get("access_token")
    ).get("user_id")

    user = data_base.query(User).filter_by(id=user_id).first()
    user_password_salt_old = user.password_salt

    response_test = client.put(
        "/api/v1/user/update_password",
        json={
            "password1": TEST_USER_PASSWORD1_UPDATE,
            "password2": TEST_USER_PASSWORD2_UPDATE,
        },
        headers={"Authorization": f"Bearer {response_login_json.get('access_token')}"},
    )

    data_base.commit()

    assert response_test.status_code == 204

    response_login = client.post(
        "/api/v1/user/login",
        data={"username": TEST_USER_ID, "password": TEST_USER_PASSWORD1_UPDATE},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert response_login.status_code == 200
    response_login_json: dict = response_login.json()
    assert response_login_json.get("access_token")
    assert response_login_json.get("token_type")

    user_id = validate_and_decode_user_access_token(
        response_login_json.get("access_token")
    ).get("user_id")

    user = data_base.query(User).filter_by(id=user_id).first()
    user_password_salt_new = user.password_salt

    assert user.name == TEST_USER_ID
    assert user.email == TEST_USER_EMAIL_UPDATE
    assert user.password != None
    assert user.password_salt != None
    assert user_password_salt_new != user_password_salt_old
    assert user.join_date != None
    assert user.is_superuser == False
    assert user.is_banned == False


engine.dispose()

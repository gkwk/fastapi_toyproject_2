from models import User
from database import session_local, engine

from fastapi.testclient import TestClient

from main import app

from pytest import MonkeyPatch

client = TestClient(app)

data_base = session_local()
data_base.query(User).delete()
data_base.commit()

def test_patch():
    def patch_task():
        a = input()
        b = input()
        return (a, b)

    fake_input = iter(["13", "39", "44", "df"]).__next__

    monkeypatch = MonkeyPatch()

    monkeypatch.setattr("builtins.input", fake_input)
    assert patch_task() == ("13", "39")
    assert patch_task() == ("44", "df")


def test_read_main():
    response = client.get("/")
    assert response.status_code == 404
    # assert response.json() == {"msg": "Hello World"}


def test_create_user():
    response = client.post(
        "/api/v1/user/create",
        json={
            "name": "test_1",
            "password1": "12345678",
            "password2": "12345678",
            "email": "test_1@test.com",
        },
    )

    assert response.status_code == 204


def test_login_user():
    response = client.post(
        "/api/v1/user/login",
        data={"username": "test_1", "password": "12345678"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    response_json: dict = response.json()
    assert response_json.get("access_token")
    assert response_json.get("token_type")


engine.dispose()

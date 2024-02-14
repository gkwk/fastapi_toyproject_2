from pytest import MonkeyPatch
import json

from fastapi.testclient import TestClient
from fastapi import WebSocket

from main import app
from domain.admin.admin_crud import create_admin_with_terminal
from models import User, Chat, ChatSession
from database import session_local
from auth import validate_and_decode_user_access_token
import v1_urn

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

TEST_CHAT_SESSION_NAME = "chat_session_name"
TEST_CHAT_SESSION_INFORMATION = "chat_session_infromation"
TEST_CHAT_SESSION_IS_VISIBLE = True
TEST_CHAT_SESSION_IS_CLOSED = False

TEST_CHAT_SESSION_NAME_UPDATE = "chat_session_name_update"
TEST_CHAT_SESSION_INFORMATION_UPDATE = "chat_session_infromation_update"
TEST_CHAT_SESSION_IS_VISIBLE_UPDATE = False
TEST_CHAT_SESSION_IS_CLOSED_UPDATE = True


TEST_CHAT_CONTENT = "chat_content"
TEST_CHAT_IS_VISIBLE = True

TEST_CHAT_CONTENT_UPDATE = "chat_content_UPDATE"
TEST_CHAT_IS_VISIBLE_UPDATE = False


URL_USER_CREATE_USER = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.USER_PREFIX, v1_urn.USER_CREATE_USER]
)

URL_USER_LOGIN_USER = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.USER_PREFIX, v1_urn.USER_LOGIN_USER]
)

URL_CHAT_CREATE_CHATSESSION = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.CHAT_PREFIX, v1_urn.CHAT_CREATE_CHATSESSION]
)
URL_CHAT_GET_CHATSESSION = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.CHAT_PREFIX, v1_urn.CHAT_GET_CHATSESSION]
)
URL_CHAT_GET_CHATSESSIONS = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.CHAT_PREFIX, v1_urn.CHAT_GET_CHATSESSIONS]
)
URL_CHAT_UPDATE_CHATSESSION = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.CHAT_PREFIX, v1_urn.CHAT_UPDATE_CHATSESSION]
)
URL_CHAT_DELETE_CHATSESSION = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.CHAT_PREFIX, v1_urn.CHAT_DELETE_CHATSESSION]
)
URL_CHAT_CREATE_CHAT = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.CHAT_PREFIX, v1_urn.CHAT_CREATE_CHAT]
)
URL_CHAT_GET_CHATS = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.CHAT_PREFIX, v1_urn.CHAT_GET_CHATS]
)
URL_CHAT_UPDATE_CHAT = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.CHAT_PREFIX, v1_urn.CHAT_UPDATE_CHAT]
)
URL_CHAT_DELETE_CHAT = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.CHAT_PREFIX, v1_urn.CHAT_DELETE_CHAT]
)

URL_CHAT_WEBSOCKET = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.CHAT_PREFIX, v1_urn.CHAT_WEBSOCKET]
)


class TestChatSession:
    def test_data_base_init(self):
        data_base = session_local()
        data_base.query(Chat).delete()
        data_base.query(ChatSession).delete()
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
            URL_USER_CREATE_USER,
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

    def test_create_chatsession(self):
        data_base = session_local()

        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        response_test = client.post(
            URL_CHAT_CREATE_CHATSESSION,
            json={
                "name": TEST_CHAT_SESSION_NAME,
                "information": TEST_CHAT_SESSION_INFORMATION,
                "is_visible": TEST_CHAT_SESSION_IS_VISIBLE,
                "is_closed": TEST_CHAT_SESSION_IS_CLOSED,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 201
        assert response_test.json() == {"result": "success"}

        chat_session = (
            data_base.query(ChatSession).filter_by(name=TEST_CHAT_SESSION_NAME).first()
        )

        assert chat_session.name == TEST_CHAT_SESSION_NAME
        assert chat_session.information == TEST_CHAT_SESSION_INFORMATION
        assert chat_session.is_visible == TEST_CHAT_SESSION_IS_VISIBLE
        assert chat_session.is_closed == TEST_CHAT_SESSION_IS_CLOSED

        data_base.close()

    def test_get_chatsession(self):
        data_base = session_local()

        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        chat_session = (
            data_base.query(ChatSession).filter_by(name=TEST_CHAT_SESSION_NAME).first()
        )

        response_test = client.get(
            URL_CHAT_GET_CHATSESSION,
            params={
                "chatting_room_id": chat_session.id,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        assert response_test_json.get("name") == TEST_CHAT_SESSION_NAME
        assert response_test_json.get("information") == TEST_CHAT_SESSION_INFORMATION
        assert response_test_json.get("is_visible") == TEST_CHAT_SESSION_IS_VISIBLE
        assert response_test_json.get("is_closed") == TEST_CHAT_SESSION_IS_CLOSED

        data_base.close()

    def test_get_chatsessions(self):
        data_base = session_local()

        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=response_login_json.get("access_token")
        ).get("user_id")

        response_test = client.get(
            URL_CHAT_GET_CHATSESSIONS,
            params={
                "user_create_id": user_id,
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

        for chat_session in response_test_json.get("chat_sesstions"):
            chat_session: dict

            assert chat_session.get("name") != None
            assert chat_session.get("information") != None
            assert chat_session.get("is_visible") != None
            assert chat_session.get("is_closed") != None

        data_base.close()

    def test_update_post(self):
        data_base = session_local()

        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        chat_session = (
            data_base.query(ChatSession).filter_by(name=TEST_CHAT_SESSION_NAME).first()
        )

        response_test = client.put(
            URL_CHAT_UPDATE_CHATSESSION,
            json={
                "id": chat_session.id,
                "name": TEST_CHAT_SESSION_NAME_UPDATE,
                "information": TEST_CHAT_SESSION_INFORMATION_UPDATE,
                "is_visible": TEST_CHAT_SESSION_IS_VISIBLE_UPDATE,
                "is_closed": TEST_CHAT_SESSION_IS_CLOSED_UPDATE,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        data_base.commit()

        assert response_test.status_code == 204

        assert chat_session.name == TEST_CHAT_SESSION_NAME_UPDATE
        assert chat_session.information == TEST_CHAT_SESSION_INFORMATION_UPDATE
        assert chat_session.is_visible == TEST_CHAT_SESSION_IS_VISIBLE_UPDATE
        assert chat_session.is_closed == TEST_CHAT_SESSION_IS_CLOSED_UPDATE

        data_base.close()

    def test_delete_post(self):
        data_base = session_local()

        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        chat_session = (
            data_base.query(ChatSession)
            .filter_by(name=TEST_CHAT_SESSION_NAME_UPDATE)
            .first()
        )

        response_test = client.delete(
            URL_CHAT_DELETE_CHATSESSION,
            params={
                "id": chat_session.id,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        data_base.commit()

        assert response_test.status_code == 204

        chat_session = (
            data_base.query(ChatSession)
            .filter_by(name=TEST_CHAT_SESSION_NAME_UPDATE)
            .first()
        )

        assert chat_session == None

        data_base.close()


class TestChat:
    def test_data_base_init(self):
        data_base = session_local()
        data_base.query(Chat).delete()
        data_base.query(ChatSession).delete()
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
            URL_USER_CREATE_USER,
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

    def test_create_chatsession(self):
        data_base = session_local()

        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        response_test = client.post(
            URL_CHAT_CREATE_CHATSESSION,
            json={
                "name": TEST_CHAT_SESSION_NAME,
                "information": TEST_CHAT_SESSION_INFORMATION,
                "is_visible": TEST_CHAT_SESSION_IS_VISIBLE,
                "is_closed": TEST_CHAT_SESSION_IS_CLOSED,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 201
        assert response_test.json() == {"result": "success"}

        chat_session = (
            data_base.query(ChatSession).filter_by(name=TEST_CHAT_SESSION_NAME).first()
        )

        assert chat_session.name == TEST_CHAT_SESSION_NAME
        assert chat_session.information == TEST_CHAT_SESSION_INFORMATION
        assert chat_session.is_visible == TEST_CHAT_SESSION_IS_VISIBLE
        assert chat_session.is_closed == TEST_CHAT_SESSION_IS_CLOSED

        data_base.close()

    def test_create_chat(self):
        data_base = session_local()

        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        chat_session = (
            data_base.query(ChatSession).filter_by(name=TEST_CHAT_SESSION_NAME).first()
        )

        response_test = client.post(
            URL_CHAT_CREATE_CHAT,
            json={
                "content": TEST_CHAT_CONTENT,
                "chat_session_id": chat_session.id,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 201
        assert response_test.json() == {"result": "success"}

        chat = (
            data_base.query(Chat)
            .filter_by(chat_session_id=chat_session.id, content=TEST_CHAT_CONTENT)
            .first()
        )

        assert chat.content == TEST_CHAT_CONTENT
        assert chat.is_visible == TEST_CHAT_IS_VISIBLE

        data_base.close()

    def test_get_chats(self):
        data_base = session_local()

        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        chat_session = (
            data_base.query(ChatSession).filter_by(name=TEST_CHAT_SESSION_NAME).first()
        )

        response_test = client.get(
            URL_CHAT_GET_CHATS,
            params={
                "chat_session_id": chat_session.id,
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

        for chat in response_test_json.get("chats"):
            chat: dict

            assert chat.get("content") != None
            assert chat.get("is_visible") != None

        data_base.close()

    def test_update_chat(self):
        data_base = session_local()

        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        chat_session = (
            data_base.query(ChatSession).filter_by(name=TEST_CHAT_SESSION_NAME).first()
        )

        chat = (
            data_base.query(Chat)
            .filter_by(
                chat_session_id=chat_session.id,
                content=TEST_CHAT_CONTENT,
            )
            .first()
        )

        response_test = client.put(
            URL_CHAT_UPDATE_CHAT,
            json={
                "id": chat.id,
                "chat_session_id": chat_session.id,
                "content": TEST_CHAT_CONTENT_UPDATE,
                "is_visible": TEST_CHAT_IS_VISIBLE_UPDATE,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        data_base.commit()

        assert response_test.status_code == 204

        assert chat.content == TEST_CHAT_CONTENT_UPDATE
        assert chat.is_visible == TEST_CHAT_IS_VISIBLE_UPDATE

        data_base.close()

    def test_delete_chat(self):
        data_base = session_local()

        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        chat_session = (
            data_base.query(ChatSession).filter_by(name=TEST_CHAT_SESSION_NAME).first()
        )

        chat = (
            data_base.query(Chat)
            .filter_by(
                chat_session_id=chat_session.id,
                content=TEST_CHAT_CONTENT_UPDATE,
            )
            .first()
        )

        response_test = client.delete(
            URL_CHAT_DELETE_CHAT,
            params={
                "id": chat.id,
                "chat_session_id": chat_session.id,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        data_base.commit()

        assert response_test.status_code == 204

        chat = (
            data_base.query(Chat)
            .filter_by(
                chat_session_id=chat_session.id,
                content=TEST_CHAT_CONTENT_UPDATE,
            )
            .first()
        )

        assert chat == None

        data_base.close()

    def test_websocket_test_endpoint(self):
        data_base = session_local()

        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=response_login_json.get("access_token")
        ).get("user_id")

        chat_session = (
            data_base.query(ChatSession).filter_by(name=TEST_CHAT_SESSION_NAME).first()
        )

        with client.websocket_connect(
            URL_CHAT_WEBSOCKET + f"/{chat_session.id}/{user_id}",
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        ) as websocket:
            websocket: WebSocket

            data = websocket.receive_json()
            websocket.send_json({"message": "websocket_test_message"})

            assert data.get("message") != None

        data_base.close()

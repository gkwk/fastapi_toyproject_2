from pytest import MonkeyPatch
import json
import pytest

from fastapi.testclient import TestClient
from httpx import Response
from fastapi import WebSocket

from main import app
from domain.admin.admin_crud import create_admin_with_terminal
from models import User, Chat, ChatSession
from database import session_local
from auth import validate_and_decode_user_access_token
import v1_urn
from domain.user.test_user import user_test_methods
from domain.admin.test_admin import admin_test_methods
from test_main import main_test_methods


client = TestClient(app)


url_dict = {
    "URL_USER_CREATE_USER": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.USER_PREFIX,
        v1_urn.USER_CREATE_USER,
    ],
    "URL_USER_LOGIN_USER": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.USER_PREFIX,
        v1_urn.USER_LOGIN_USER,
    ],
    "URL_CHAT_CREATE_CHATSESSION": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.CHAT_PREFIX,
        v1_urn.CHAT_CREATE_CHATSESSION,
    ],
    "URL_CHAT_GET_CHATSESSION": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.CHAT_PREFIX,
        v1_urn.CHAT_GET_CHATSESSION,
    ],
    "URL_CHAT_GET_CHATSESSIONS": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.CHAT_PREFIX,
        v1_urn.CHAT_GET_CHATSESSIONS,
    ],
    "URL_CHAT_UPDATE_CHATSESSION": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.CHAT_PREFIX,
        v1_urn.CHAT_UPDATE_CHATSESSION,
    ],
    "URL_CHAT_DELETE_CHATSESSION": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.CHAT_PREFIX,
        v1_urn.CHAT_DELETE_CHATSESSION,
    ],
    "URL_CHAT_CREATE_CHAT": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.CHAT_PREFIX,
        v1_urn.CHAT_CREATE_CHAT,
    ],
    "URL_CHAT_GET_CHATS": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.CHAT_PREFIX,
        v1_urn.CHAT_GET_CHATS,
    ],
    "URL_CHAT_UPDATE_CHAT": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.CHAT_PREFIX,
        v1_urn.CHAT_UPDATE_CHAT,
    ],
    "URL_CHAT_DELETE_CHAT": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.CHAT_PREFIX,
        v1_urn.CHAT_DELETE_CHAT,
    ],
    "URL_CHAT_WEBSOCKET": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.CHAT_PREFIX,
        v1_urn.CHAT_WEBSOCKET,
    ],
}

test_parameter_dict = {
    "test_create_admin": {
        "argnames": "name, password1, password2, email",
        "argvalues": [
            (f"admin{i}", "12345678", "12345678", f"admin{i}@test.com")
            for i in range(10)
        ],
    },
    "test_create_user": {
        "argnames": "name, password1, password2, email",
        "argvalues": [
            (f"user{i}", "12345678", "12345678", f"user{i}@test.com") for i in range(20)
        ],
    },
    "test_create_chatsession": {
        "argnames": "admin_name, admin_password1, chatsession_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "chat_session_name": f"chat_session_{i}_{j}",
                        "chat_session_information": f"chat_session_{i}_{j}_information",
                        "chat_session_is_visible": True,
                        "chat_session_is_closed": False,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_get_chatsession": {
        "argnames": "name, password1, chatsession_id_list, chatsession_columns",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [1 + (i * 2) + j for j in range(2)],
                ["name", "information", "is_visible", "is_closed"],
            )
            for i in range(10)
        ],
    },
    "test_get_chatsessions": {
        "argnames": "name, password1, chatsessions_params, chatsession_columns",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                {
                    "user_create_id": None,
                    "chat_session_skip": None,
                    "chat_session_limit": 100,
                },
                ["name", "information", "is_visible", "is_closed"],
            )
            for i in range(10)
        ],
    },
    "test_update_chatsession": {
        "argnames": "name, password1, chatsession_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "chatsession_id": 1 + (i * 2) + j,
                        "chatsession_name": f"chat_session_{i}_{j}_admin{i}_update",
                        "chatsession_information": f"chat_session_{i}_{j}_admin{i}_content_update",
                        "chatsession_is_visible": None,
                        "chatsession_is_closed": None,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_delete_chatsession": {
        "argnames": "name, password1, chatsession_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "chatsession_id": 1 + (i * 2) + j,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_create_chat": {
        "argnames": "admin_name, admin_password1, chat_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "chat_content": f"chat_{i}_{j}_content",
                        "chat_session_id": 1 + (i * 2) + j,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_get_chats": {
        "argnames": "name, password1, chats_params, chat_columns",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                {
                    "chat_session_id": 1 + (i * 2),
                    "chat_skip": None,
                    "chat_limit": 100,
                },
                ["content", "is_visible"],
            )
            for i in range(10)
        ],
    },
    "test_update_chat": {
        "argnames": "name, password1, chat_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "chat_id": 1 + (i * 2) + j,
                        "chat_session_id": 1 + (i * 2) + j,
                        "chat_content": f"chat_{i}_{j}_admin{i}_content_update",
                        "chat_is_visible": None,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_delete_chat": {
        "argnames": "name, password1, chat_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "chat_id": 1 + (i * 2) + j,
                        "chat_session_id": 1 + (i * 2) + j,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_websocket_test_endpoint": {
        "argnames": "name, password1, chat_content, chat_session_id",
        "argvalues": [
            (f"admin{i}", "12345678", "12345678", 1 + (i * 2)) for i in range(10)
        ],
    },
}


URL_USER_CREATE_USER = "".join(url_dict.get("URL_USER_CREATE_USER"))
URL_USER_LOGIN_USER = "".join(url_dict.get("URL_USER_LOGIN_USER"))
URL_CHAT_CREATE_CHATSESSION = "".join(url_dict.get("URL_CHAT_CREATE_CHATSESSION"))
URL_CHAT_GET_CHATSESSION = "".join(url_dict.get("URL_CHAT_GET_CHATSESSION"))
URL_CHAT_GET_CHATSESSIONS = "".join(url_dict.get("URL_CHAT_GET_CHATSESSIONS"))
URL_CHAT_UPDATE_CHATSESSION = "".join(url_dict.get("URL_CHAT_UPDATE_CHATSESSION"))
URL_CHAT_DELETE_CHATSESSION = "".join(url_dict.get("URL_CHAT_DELETE_CHATSESSION"))
URL_CHAT_CREATE_CHAT = "".join(url_dict.get("URL_CHAT_CREATE_CHAT"))
URL_CHAT_GET_CHATS = "".join(url_dict.get("URL_CHAT_GET_CHATS"))
URL_CHAT_UPDATE_CHAT = "".join(url_dict.get("URL_CHAT_UPDATE_CHAT"))
URL_CHAT_DELETE_CHAT = "".join(url_dict.get("URL_CHAT_DELETE_CHAT"))
URL_CHAT_WEBSOCKET = "".join(url_dict.get("URL_CHAT_WEBSOCKET"))


class ChatSessionTestMethods:
    def create_chatsession(
        self,
        chat_session_name,
        chat_session_information,
        chat_session_is_visible,
        chat_session_is_closed,
        access_token: str,
    ):

        response_test = client.post(
            URL_CHAT_CREATE_CHATSESSION,
            json={
                "name": chat_session_name,
                "information": chat_session_information,
                "is_visible": chat_session_is_visible,
                "is_closed": chat_session_is_closed,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def create_chatsession_test(
        self,
        chat_session_name,
        chat_session_information,
        chat_session_is_visible,
        chat_session_is_closed,
        access_token: str,
        response_test: Response,
    ):
        data_base = session_local()

        assert response_test.status_code == 201
        assert response_test.json() == {"result": "success"}

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=access_token
        ).get("user_id")
        chat_session = (
            data_base.query(ChatSession)
            .filter_by(user_create_id=user_id, name=chat_session_name)
            .first()
        )

        assert chat_session.name == chat_session_name
        assert chat_session.information == chat_session_information
        assert chat_session.is_visible == chat_session_is_visible
        assert chat_session.is_closed == chat_session_is_closed
        assert chat_session.create_date != None
        assert chat_session.update_date == None

        data_base.close()

    def get_chatsession(self, chat_session_id, access_token: str):

        response_test = client.get(
            URL_CHAT_GET_CHATSESSION,
            params={
                "chatting_room_id": chat_session_id,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def get_chatsession_test(self, chat_session_columns, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        for chat_session_column in chat_session_columns:
            assert chat_session_column in response_test_json

        data_base.close()

    def get_chatsessions(
        self, user_create_id, chat_session_skip, chat_session_limit, access_token: str
    ):
        params = {}
        if user_create_id != None:
            params["user_create_id"] = user_create_id
        if chat_session_skip != None:
            params["skip"] = chat_session_skip
        if chat_session_limit != None:
            params["limit"] = chat_session_limit

        response_test = client.get(
            URL_CHAT_GET_CHATSESSIONS,
            params=params,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def get_chatsessions_test(self, chat_session_columns, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        assert response_test_json.get("total") >= 0

        for chat_session in response_test_json.get("chat_sessions"):
            chat_session: dict

            for chat_session_column in chat_session_columns:
                assert chat_session_column in chat_session

        data_base.close()

    def update_chatsession(
        self,
        chatsession_id,
        chatsession_name,
        chatsession_information,
        chatsession_is_visible,
        chatsession_is_closed,
        access_token: str,
    ):
        response_test = client.put(
            URL_CHAT_UPDATE_CHATSESSION,
            json={
                "id": chatsession_id,
                "name": chatsession_name,
                "information": chatsession_information,
                "is_visible": chatsession_is_visible,
                "is_closed": chatsession_is_closed,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def update_chatsession_test(
        self,
        chatsession_id,
        chatsession_name,
        chatsession_information,
        chatsession_is_visible,
        chatsession_is_closed,
        response_test: Response,
    ):
        data_base = session_local()

        assert response_test.status_code == 204

        chat_session = data_base.query(ChatSession).filter_by(id=chatsession_id).first()

        if chatsession_name != None:
            assert chat_session.name == chatsession_name
        if chatsession_information != None:
            assert chat_session.information == chatsession_information
        if chatsession_is_visible != None:
            assert chat_session.is_visible == chatsession_is_visible
        if chatsession_is_closed != None:
            assert chat_session.is_closed == chatsession_is_closed

        data_base.close()

    def delete_chatsession(self, chatsession_id, access_token: str):
        response_test = client.delete(
            URL_CHAT_DELETE_CHATSESSION,
            params={
                "id": chatsession_id,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def delete_chatsession_test(self, chatsession_id, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 204

        chat_session = data_base.query(ChatSession).filter_by(id=chatsession_id).first()

        assert chat_session == None

        data_base.close()


class ChatTestMethods:
    def create_chat(
        self,
        chat_content,
        chat_session_id,
        access_token: str,
    ):

        response_test = client.post(
            URL_CHAT_CREATE_CHAT,
            json={
                "content": chat_content,
                "chat_session_id": chat_session_id,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def create_chat_test(
        self,
        chat_content,
        chat_session_id,
        access_token: str,
        response_test: Response,
    ):
        data_base = session_local()

        assert response_test.status_code == 201
        assert response_test.json() == {"result": "success"}

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=access_token
        ).get("user_id")

        chat = (
            data_base.query(Chat)
            .filter_by(
                user_id=user_id, chat_session_id=chat_session_id, content=chat_content
            )
            .first()
        )

        assert chat.content == chat_content
        assert chat.is_visible == True

        data_base.close()

    def get_chats(self, chat_session_id, chat_skip, chat_limit, access_token: str):
        params = {}
        if chat_session_id != None:
            params["chat_session_id"] = chat_session_id
        if chat_skip != None:
            params["skip"] = chat_skip
        if chat_limit != None:
            params["limit"] = chat_limit

        response_test = client.get(
            URL_CHAT_GET_CHATS,
            params=params,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return response_test

    def get_chats_test(self, chat_columns, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        assert response_test_json.get("total") >= 0

        for chat in response_test_json.get("chats"):
            chat: dict

            for chat_column in chat_columns:
                assert chat_column in chat

        data_base.close()

    def update_chat(
        self,
        chat_id,
        chat_session_id,
        chat_content,
        chat_is_visible,
        access_token: str,
    ):
        response_test = client.put(
            URL_CHAT_UPDATE_CHAT,
            json={
                "id": chat_id,
                "chat_session_id": chat_session_id,
                "content": chat_content,
                "is_visible": chat_is_visible,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def update_chat_test(
        self,
        chat_id,
        chat_session_id,
        chat_content,
        chat_is_visible,
        response_test: Response,
    ):
        data_base = session_local()

        assert response_test.status_code == 204

        chat = (
            data_base.query(Chat)
            .filter_by(
                chat_session_id=chat_session_id,
                id=chat_id,
            )
            .first()
        )

        if chat_content != None:
            assert chat.content == chat_content
        if chat_is_visible != None:
            assert chat.is_visible == chat_is_visible

        data_base.close()

    def delete_chat(self, chat_id, chat_session_id, access_token: str):
        response_test = client.delete(
            URL_CHAT_DELETE_CHAT,
            params={
                "id": chat_id,
                "chat_session_id": chat_session_id,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def delete_chat_test(self, chat_id, chat_session_id, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 204

        chat = (
            data_base.query(Chat)
            .filter_by(
                chat_session_id=chat_session_id,
                id=chat_id,
            )
            .first()
        )

        assert chat == None

        data_base.close()

    def websocket_test_endpoint(
        self,
        chat_content,
        chat_session_id,
        access_token: str,
    ):
        data_base = session_local()

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=access_token
        ).get("user_id")

        with client.websocket_connect(
            URL_CHAT_WEBSOCKET + f"/{chat_session_id}/{user_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        ) as websocket:
            websocket: WebSocket

            response_receive_test = websocket.receive_json()
            websocket.send_json({"message": chat_content})

        data_base.close()

        return response_receive_test

    def websocket_test_endpoint_test(
        self,
        chat_content,
        chat_session_id,
        response_receive_test: dict,
    ):
        data_base = session_local()

        assert response_receive_test.get("message") != None
        chat = (
            data_base.query(Chat)
            .filter_by(
                chat_session_id=chat_session_id,
                content=chat_content,
            )
            .first()
        )

        assert chat != None

        data_base.close()


chat_session_test_methods = ChatSessionTestMethods()
chat_test_methods = ChatTestMethods()


class TestChatSession:
    def test_data_base_init(self):
        main_test_methods.data_base_init()

    @pytest.mark.parametrize(**test_parameter_dict["test_create_admin"])
    def test_create_admin(self, name, password1, password2, email):
        admin_test_methods.create_admin(name, password1, password2, email)
        admin_test_methods.create_admin_test(name, password1, email)

    @pytest.mark.parametrize(**test_parameter_dict["test_create_user"])
    def test_create_user(self, name, password1, password2, email):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        user_test_methods.create_user_test(response_test, name, password1, email)

    @pytest.mark.parametrize(**test_parameter_dict["test_create_chatsession"])
    def test_create_chatsession(self, admin_name, admin_password1, chatsession_args):
        response_login = user_test_methods.login_user(admin_name, admin_password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for chatsession_arg in chatsession_args:
            response_test = chat_session_test_methods.create_chatsession(
                **chatsession_arg, access_token=access_token
            )
            chat_session_test_methods.create_chatsession_test(
                **chatsession_arg,
                access_token=access_token,
                response_test=response_test,
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_get_chatsession"])
    def test_get_chatsession(
        self, name, password1, chatsession_id_list, chatsession_columns
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for chatsession_id in chatsession_id_list:
            response_test = chat_session_test_methods.get_chatsession(
                chatsession_id, access_token=access_token
            )
            chat_session_test_methods.get_chatsession_test(
                chatsession_columns, response_test=response_test
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_get_chatsessions"])
    def test_get_chatsessions(
        self, name, password1, chatsessions_params, chatsession_columns
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = chat_session_test_methods.get_chatsessions(
            **chatsessions_params, access_token=access_token
        )
        chat_session_test_methods.get_chatsessions_test(
            chatsession_columns, response_test=response_test
        )

    @pytest.mark.parametrize(**test_parameter_dict["test_update_chatsession"])
    def test_update_chatsession(
        self,
        name,
        password1,
        chatsession_args,
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for chatsession_arg in chatsession_args:
            response_test = chat_session_test_methods.update_chatsession(
                **chatsession_arg, access_token=access_token
            )
            chat_session_test_methods.update_chatsession_test(
                **chatsession_arg, response_test=response_test
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_delete_chatsession"])
    def test_delete_chatsession(self, name, password1, chatsession_args):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for chatsession_arg in chatsession_args:
            response_test = chat_session_test_methods.delete_chatsession(
                **chatsession_arg, access_token=access_token
            )
            chat_session_test_methods.delete_chatsession_test(
                **chatsession_arg, response_test=response_test
            )


class TestChat:
    def test_data_base_init(self):
        main_test_methods.data_base_init()

    @pytest.mark.parametrize(**test_parameter_dict["test_create_admin"])
    def test_create_admin(self, name, password1, password2, email):
        admin_test_methods.create_admin(name, password1, password2, email)
        admin_test_methods.create_admin_test(name, password1, email)

    @pytest.mark.parametrize(**test_parameter_dict["test_create_user"])
    def test_create_user(self, name, password1, password2, email):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        user_test_methods.create_user_test(response_test, name, password1, email)

    @pytest.mark.parametrize(**test_parameter_dict["test_create_chatsession"])
    def test_create_chatsession(self, admin_name, admin_password1, chatsession_args):
        response_login = user_test_methods.login_user(admin_name, admin_password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for chatsession_arg in chatsession_args:
            response_test = chat_session_test_methods.create_chatsession(
                **chatsession_arg, access_token=access_token
            )
            chat_session_test_methods.create_chatsession_test(
                **chatsession_arg,
                access_token=access_token,
                response_test=response_test,
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_create_chat"])
    def test_create_chat(self, admin_name, admin_password1, chat_args):
        response_login = user_test_methods.login_user(admin_name, admin_password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for chat_arg in chat_args:
            response_test = chat_test_methods.create_chat(
                **chat_arg, access_token=access_token
            )
            chat_test_methods.create_chat_test(
                **chat_arg,
                access_token=access_token,
                response_test=response_test,
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_get_chats"])
    def test_get_chats(self, name, password1, chats_params, chat_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = chat_test_methods.get_chats(
            **chats_params, access_token=access_token
        )
        chat_test_methods.get_chats_test(chat_columns, response_test=response_test)

    @pytest.mark.parametrize(**test_parameter_dict["test_update_chat"])
    def test_update_chat(
        self,
        name,
        password1,
        chat_args,
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for chat_arg in chat_args:
            response_test = chat_test_methods.update_chat(
                **chat_arg, access_token=access_token
            )
            chat_test_methods.update_chat_test(**chat_arg, response_test=response_test)

    @pytest.mark.parametrize(**test_parameter_dict["test_delete_chat"])
    def test_delete_chat(self, name, password1, chat_args):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for chat_arg in chat_args:
            response_test = chat_test_methods.delete_chat(
                **chat_arg, access_token=access_token
            )
            chat_test_methods.delete_chat_test(**chat_arg, response_test=response_test)

    @pytest.mark.parametrize(**test_parameter_dict["test_websocket_test_endpoint"])
    def test_websocket_test_endpoint(
        self, name, password1, chat_content, chat_session_id
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_receive_test = chat_test_methods.websocket_test_endpoint(
            chat_content, chat_session_id, access_token=access_token
        )
        chat_test_methods.websocket_test_endpoint_test(
            chat_content,
            chat_session_id,
            response_receive_test=response_receive_test,
        )

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


def parameter_data_loader(path):
    test_data = {"argnames": None, "argvalues": []}

    with open(path, "r", encoding="UTF-8") as f:
        json_data: dict = json.load(f)

    test_data["argnames"] = "pn," + json_data.get("argnames")

    for value in json_data.get("argvalues_pass", []):
        test_data["argvalues"].append(tuple([1, *value]))

    for value in json_data.get("argvalues_fail", []):
        value_temp = pytest.param(
            0, *value[:-1], marks=pytest.mark.xfail(reason=value[-1])
        )
        test_data["argvalues"].append(value_temp)

    return test_data


ID_DICT_ADMIN_ID = "admin_id"
ID_DICT_USER_ID = "user_id"
ID_DICT_CHATSESSION_ID = "chatsession_id"
ID_DICT_CHAT_ID = "chat_id"


id_list_dict = {
    ID_DICT_ADMIN_ID: [],
    ID_DICT_USER_ID: [],
    ID_DICT_CHATSESSION_ID: [],
    ID_DICT_CHAT_ID: [],
}

id_iterator_dict = {
    ID_DICT_ADMIN_ID: iter([]),
    ID_DICT_USER_ID: iter([]),
    ID_DICT_CHATSESSION_ID: iter([]),
    ID_DICT_CHAT_ID: iter([]),
}


def id_list_append(id_dict_str, value):
    id_list_dict[id_dict_str].append(value)


def id_iterator_next(pn, id_dict_str) -> int | None:
    if pn:
        try:
            next_id = id_iterator_dict[id_dict_str].__next__()
        except StopIteration:
            id_iterator_dict[id_dict_str] = iter(id_list_dict[id_dict_str])
            next_id = id_iterator_dict[id_dict_str].__next__()

        return next_id

    return None


def id_list_clear(id_dict_str):
    id_list_dict[id_dict_str] = []


def id_iterator_clear(id_dict_str):
    id_iterator_dict[id_dict_str] = iter(id_list_dict[id_dict_str])


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
        response_test_json: dict = response_test.json()
        assert response_test_json.get("result")
        assert response_test_json.get("id") > 0

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=access_token
        ).get("user_id")
        chat_session = (
            data_base.query(ChatSession)
            .filter_by(user_create_id=user_id, id=response_test_json.get("id"))
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

        assert set(chat_session_columns) == set(response_test_json.keys())

        data_base.close()

    def get_chatsessions(
        self,
        *,
        user_create_id,
        chat_session_skip=None,
        chat_session_limit=None,
        access_token: str,
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
            assert set(chat_session_columns) == set(chat_session.keys())

        data_base.close()

    def update_chatsession(
        self,
        *,
        chatsession_id,
        chatsession_name=None,
        chatsession_information=None,
        chatsession_is_visible=None,
        chatsession_is_closed=None,
        access_token: str,
    ):
        params = {}
        if chatsession_name != None:
            params["name"] = chatsession_name
        if chatsession_information != None:
            params["information"] = chatsession_information
        if chatsession_is_visible != None:
            params["is_visible"] = chatsession_is_visible
        if chatsession_is_closed != None:
            params["is_closed"] = chatsession_is_closed

        response_test = client.put(
            URL_CHAT_UPDATE_CHATSESSION,
            json={"id": chatsession_id, **params},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def update_chatsession_test(
        self,
        *,
        chatsession_id,
        chatsession_name=None,
        chatsession_information=None,
        chatsession_is_visible=None,
        chatsession_is_closed=None,
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
        response_test_json: dict = response_test.json()
        assert response_test_json.get("result")
        assert response_test_json.get("id") > 0

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=access_token
        ).get("user_id")

        chat = (
            data_base.query(Chat)
            .filter_by(
                user_id=user_id,
                chat_session_id=chat_session_id,
                id=response_test_json.get("id"),
            )
            .first()
        )

        assert chat.content == chat_content
        assert chat.is_visible == True

        data_base.close()

    def get_chats(
        self, *, chat_session_id, chat_skip=None, chat_limit=None, access_token: str
    ):
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

            assert set(chat_columns) == set(chat.keys())

        data_base.close()

    def update_chat(
        self,
        *,
        chat_id,
        chat_session_id,
        chat_content=None,
        chat_is_visible=None,
        access_token: str,
    ):
        params = {}
        if chat_content != None:
            params["content"] = chat_content
        if chat_is_visible != None:
            params["is_visible"] = chat_is_visible

        response_test = client.put(
            URL_CHAT_UPDATE_CHAT,
            json={"id": chat_id, "chat_session_id": chat_session_id, **params},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def update_chat_test(
        self,
        *,
        chat_id,
        chat_session_id,
        chat_content=None,
        chat_is_visible=None,
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
        for id in id_list_dict:
            id_list_clear(id)
            id_iterator_clear(id)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/chat/test_create_admin.json")
    )
    def test_create_admin(self, pn, name, password1, password2, email):
        admin_id = admin_test_methods.create_admin(name, password1, password2, email)
        id_list_append(ID_DICT_ADMIN_ID, admin_id)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/chat/test_create_user.json")
    )
    def test_create_user(self, pn, name, password1, password2, email):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        id_list_append(ID_DICT_USER_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/chat/test_create_chatsession.json")
    )
    def test_create_chatsession(self, pn, name, password1, chatsession_arg):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = chat_session_test_methods.create_chatsession(
            **chatsession_arg, access_token=access_token
        )
        chat_session_test_methods.create_chatsession_test(
            **chatsession_arg,
            access_token=access_token,
            response_test=response_test,
        )
        id_list_append(ID_DICT_CHATSESSION_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/chat/test_get_chatsession.json")
    )
    def test_get_chatsession(self, pn, name, password1, chatsession_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        chatsession_id = id_iterator_next(pn, ID_DICT_CHATSESSION_ID)

        response_test = chat_session_test_methods.get_chatsession(
            chatsession_id, access_token=access_token
        )
        chat_session_test_methods.get_chatsession_test(
            chatsession_columns, response_test=response_test
        )

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/chat/test_get_chatsessions.json")
    )
    def test_get_chatsessions(
        self, pn, name, password1, chatsessions_params, chatsession_columns
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        user_id = id_iterator_next(pn, ID_DICT_ADMIN_ID)

        response_test = chat_session_test_methods.get_chatsessions(
            user_create_id=user_id, **chatsessions_params, access_token=access_token
        )
        chat_session_test_methods.get_chatsessions_test(
            chatsession_columns, response_test=response_test
        )

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/chat/test_update_chatsession.json")
    )
    def test_update_chatsession(
        self,
        pn,
        name,
        password1,
        chatsession_arg,
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        chatsession_id = id_iterator_next(pn, ID_DICT_CHATSESSION_ID)

        response_test = chat_session_test_methods.update_chatsession(
            chatsession_id=chatsession_id, **chatsession_arg, access_token=access_token
        )
        chat_session_test_methods.update_chatsession_test(
            chatsession_id=chatsession_id,
            **chatsession_arg,
            response_test=response_test,
        )

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/chat/test_delete_chatsession.json")
    )
    def test_delete_chatsession(self, pn, name, password1):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        chatsession_id = id_iterator_next(pn, ID_DICT_CHATSESSION_ID)

        response_test = chat_session_test_methods.delete_chatsession(
            chatsession_id=chatsession_id, access_token=access_token
        )
        chat_session_test_methods.delete_chatsession_test(
            chatsession_id=chatsession_id, response_test=response_test
        )


class TestChat:
    def test_data_base_init(self):
        main_test_methods.data_base_init()
        for id in id_list_dict:
            id_list_clear(id)
            id_iterator_clear(id)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/chat/test_create_admin.json")
    )
    def test_create_admin(self, pn, name, password1, password2, email):
        admin_id = admin_test_methods.create_admin(name, password1, password2, email)
        id_list_append(ID_DICT_ADMIN_ID, admin_id)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/chat/test_create_user.json")
    )
    def test_create_user(self, pn, name, password1, password2, email):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        id_list_append(ID_DICT_USER_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/chat/test_create_chatsession.json")
    )
    def test_create_chatsession(self, pn, name, password1, chatsession_arg):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = chat_session_test_methods.create_chatsession(
            **chatsession_arg, access_token=access_token
        )
        chat_session_test_methods.create_chatsession_test(
            **chatsession_arg,
            access_token=access_token,
            response_test=response_test,
        )
        id_list_append(ID_DICT_CHATSESSION_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/chat/test_create_chat.json")
    )
    def test_create_chat(self, pn, name, password1, chat_arg):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")
        chat_session_id = id_iterator_next(pn, ID_DICT_CHATSESSION_ID)

        response_test = chat_test_methods.create_chat(
            chat_session_id=chat_session_id, **chat_arg, access_token=access_token
        )
        chat_test_methods.create_chat_test(
            chat_session_id=chat_session_id,
            **chat_arg,
            access_token=access_token,
            response_test=response_test,
        )
        id_list_append(
            ID_DICT_CHAT_ID, (chat_session_id, response_test.json().get("id"))
        )

    @pytest.mark.parametrize(**parameter_data_loader("domain/chat/test_get_chats.json"))
    def test_get_chats(self, pn, name, password1, chats_params, chat_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        chat_session_id = id_iterator_next(pn, ID_DICT_CHATSESSION_ID)

        response_test = chat_test_methods.get_chats(
            chat_session_id=chat_session_id, **chats_params, access_token=access_token
        )
        chat_test_methods.get_chats_test(chat_columns, response_test=response_test)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/chat/test_update_chat.json")
    )
    def test_update_chat(
        self,
        pn,
        name,
        password1,
        chat_arg,
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        chat_session_id, chat_id = id_iterator_next(pn, ID_DICT_CHAT_ID)

        response_test = chat_test_methods.update_chat(
            chat_session_id=chat_session_id,
            chat_id=chat_id,
            **chat_arg,
            access_token=access_token,
        )
        chat_test_methods.update_chat_test(
            chat_session_id=chat_session_id,
            chat_id=chat_id,
            **chat_arg,
            response_test=response_test,
        )

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/chat/test_delete_chat.json")
    )
    def test_delete_chat(self, pn, name, password1):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")
        chat_session_id, chat_id = id_iterator_next(pn, ID_DICT_CHAT_ID)

        response_test = chat_test_methods.delete_chat(
            chat_session_id=chat_session_id, chat_id=chat_id, access_token=access_token
        )
        chat_test_methods.delete_chat_test(
            chat_session_id=chat_session_id,
            chat_id=chat_id,
            response_test=response_test,
        )

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/chat/test_websocket_test_endpoint.json")
    )
    def test_websocket_test_endpoint(self, pn, name, password1, chat_content):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        chat_session_id = id_iterator_next(pn, ID_DICT_CHATSESSION_ID)

        response_receive_test = chat_test_methods.websocket_test_endpoint(
            chat_content, chat_session_id, access_token=access_token
        )
        chat_test_methods.websocket_test_endpoint_test(
            chat_content,
            chat_session_id,
            response_receive_test=response_receive_test,
        )

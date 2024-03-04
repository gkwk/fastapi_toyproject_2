import json
from pytest import MonkeyPatch
import pytest

from fastapi.testclient import TestClient

from httpx import Response

from main import app
from domain.admin.admin_crud import create_admin_with_terminal
from models import User, Board, UserPermissionTable
from database import session_local
import v1_urn
from domain.user.test_user import user_test_methods
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
    "URL_ADMIN_GET_USERS": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.ADMIN_PREFIX,
        v1_urn.ADMIN_GET_USERS,
    ],
    "URL_ADMIN_CREATE_BOARD": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.ADMIN_PREFIX,
        v1_urn.ADMIN_CREATE_BOARD,
    ],
    "URL_ADMIN_UPDATE_USER_BOARD_PERMISSION": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.ADMIN_PREFIX,
        v1_urn.ADMIN_UPDATE_USER_BOARD_PERMISSION,
    ],
    "URL_ADMIN_UPDATE_USER_IS_BANNED": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.ADMIN_PREFIX,
        v1_urn.ADMIN_UPDATE_USER_IS_BANNED,
    ],
}


URL_USER_CREATE_USER = "".join(url_dict.get("URL_USER_CREATE_USER"))
URL_USER_LOGIN_USER = "".join(url_dict.get("URL_USER_LOGIN_USER"))
URL_ADMIN_GET_USERS = "".join(url_dict.get("URL_ADMIN_GET_USERS"))
URL_ADMIN_CREATE_BOARD = "".join(url_dict.get("URL_ADMIN_CREATE_BOARD"))
URL_ADMIN_UPDATE_USER_BOARD_PERMISSION = "".join(
    url_dict.get("URL_ADMIN_UPDATE_USER_BOARD_PERMISSION")
)
URL_ADMIN_UPDATE_USER_IS_BANNED = "".join(
    url_dict.get("URL_ADMIN_UPDATE_USER_IS_BANNED")
)


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
ID_DICT_BOARD_ID = "board_id"

id_list_dict = {
    ID_DICT_ADMIN_ID: [],
    ID_DICT_USER_ID: [],
    ID_DICT_BOARD_ID: [],
}

id_iterator_dict = {
    ID_DICT_ADMIN_ID: iter([]),
    ID_DICT_USER_ID: iter([]),
    ID_DICT_BOARD_ID: iter([]),
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


def id_iterator_clear(id_dict_str):
    id_iterator_dict[id_dict_str] = iter(id_list_dict[id_dict_str])


class AdminTestMethods:
    def create_admin(self, name, password1, password2, email):
        input_iter = iter([name, email]).__next__
        getpass_iter = iter([password1, password2]).__next__

        monkeypatch = MonkeyPatch()
        monkeypatch.setattr("builtins.input", lambda _: input_iter())
        monkeypatch.setattr("getpass.getpass", lambda _: getpass_iter())

        return create_admin_with_terminal(data_base=None, debug=True)

    def create_admin_test(self, name, password1, email):
        # create_admin 후 진행

        data_base = session_local()

        admin = data_base.query(User).filter_by(name=name, email=email).first()

        assert admin.name == name
        assert admin.email == email
        assert admin.password != password1
        assert admin.password_salt != None
        assert admin.join_date != None
        assert admin.update_date == None
        assert admin.is_superuser == True
        assert admin.is_banned == False

        data_base.close()

    def get_users(self, access_token: str):
        # 로그인 후 진행

        response_test = client.get(
            URL_ADMIN_GET_USERS,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def get_users_test(self, user_columns, response_test: Response):
        # get_users 후 진행

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        for user in response_test_json.get("users"):
            user: dict
            assert set(user_columns) == set(user.keys())

    def create_board(
        self, board_name, board_information, board_is_visible, access_token: str
    ):
        # 로그인 후 진행

        response_test = client.post(
            URL_ADMIN_CREATE_BOARD,
            json={
                "name": board_name,
                "information": board_information,
                "is_visible": board_is_visible,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def create_board_test(
        self, board_name, board_information, board_is_visible, response_test: Response
    ):
        # create_board 후 진행

        data_base = session_local()

        assert response_test.status_code == 201
        response_test_json: dict = response_test.json()
        assert response_test_json.get("result") == "success"
        assert response_test_json.get("id") > 0

        board = (
            data_base.query(Board)
            .filter_by(name=board_name, information=board_information)
            .first()
        )

        assert board.name == board_name
        assert board.information == board_information
        assert board.is_visible == board_is_visible

        data_base.close()

    def update_user_board_permission(
        self, user_id, board_id, user_is_permitted, access_token: str
    ):
        # 로그인 후 진행
        response_test = client.put(
            URL_ADMIN_UPDATE_USER_BOARD_PERMISSION,
            json={
                "user_id": user_id,
                "board_id": board_id,
                "is_permitted": user_is_permitted,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def update_user_board_permission_test(
        self, user_id, board_id, user_is_permitted, response_test: Response
    ):
        # update_user_board_permission 후 진행

        data_base = session_local()

        assert response_test.status_code == 204

        user_board_permission = (
            data_base.query(UserPermissionTable)
            .filter_by(user_id=user_id, board_id=board_id)
            .first()
        )

        if user_is_permitted:
            assert user_board_permission != None
        else:
            assert user_board_permission == None

        data_base.close()

    def update_user_is_banned(self, user_id, user_is_banned, access_token: str):
        # 로그인 후 진행

        response_test = client.put(
            URL_ADMIN_UPDATE_USER_IS_BANNED,
            json={
                "user_id": user_id,
                "is_banned": user_is_banned,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def update_user_is_banned_test(
        self, user_id, user_is_banned, response_test: Response
    ):
        # update_user_is_banned 후 진행

        data_base = session_local()

        assert response_test.status_code == 204

        user = data_base.query(User).filter_by(id=user_id).first()

        assert user.is_banned == user_is_banned
        data_base.close()


admin_test_methods = AdminTestMethods()


class TestAdmin:
    def test_data_base_init(self):
        main_test_methods.data_base_init()

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/admin/test_create_admin.json")
    )
    def test_create_admin(self, pn, name, password1, password2, email):
        admin_id = admin_test_methods.create_admin(name, password1, password2, email)
        admin_test_methods.create_admin_test(name, password1, email)

        id_list_append(ID_DICT_ADMIN_ID, admin_id)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/admin/test_create_user.json")
    )
    def test_create_user(self, pn, name, password1, password2, email):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        id_list_append(ID_DICT_USER_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/admin/test_get_users.json")
    )
    def test_get_users(self, pn, name, password1, user_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = admin_test_methods.get_users(access_token)
        admin_test_methods.get_users_test(user_columns, response_test)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/admin/test_create_board.json")
    )
    def test_create_board(self, pn, admin_name, admin_password1, board_args):
        for board_arg in board_args:
            response_login = user_test_methods.login_user(admin_name, admin_password1)
            response_login_json: dict = response_login.json()
            access_token = response_login_json.get("access_token")

            response_test = admin_test_methods.create_board(
                **board_arg, access_token=access_token
            )
            admin_test_methods.create_board_test(
                **board_arg, response_test=response_test
            )
            id_list_append(ID_DICT_BOARD_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/admin/test_update_user_board_permission.json")
    )
    def test_update_user_board_permission(self, pn, name, password1, test_args):

        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        user_id = id_iterator_next(pn, ID_DICT_USER_ID)
        board_id = id_iterator_next(pn, ID_DICT_BOARD_ID)


        for test_arg in test_args:
            args_dict = {}
        
            if pn:
                args_dict["user_id"] = user_id
                args_dict["board_id"] = board_id


            
            response_test = admin_test_methods.update_user_board_permission(
                user_id=user_id,
                board_id=board_id,
                **test_arg,
                access_token=access_token,
            )
            admin_test_methods.update_user_board_permission_test(
                user_id=user_id,
                board_id=board_id,
                **test_arg,
                response_test=response_test,
            )

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/admin/test_update_user_is_banned.json")
    )
    def test_update_user_is_banned(self, pn, name, password1, test_args):

        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        user_id = id_iterator_next(pn, ID_DICT_USER_ID)

        for test_arg in test_args:

            response_test = admin_test_methods.update_user_is_banned(
                user_id=user_id, **test_arg, access_token=access_token
            )
            admin_test_methods.update_user_is_banned_test(
                user_id=user_id, **test_arg, response_test=response_test
            )

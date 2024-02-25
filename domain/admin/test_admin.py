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

test_parameter_dict = {
    "test_create_admin": {
        "argnames": "name, password1, password2, email",
        "argvalues": [
            (f"admin{i}", "12345678", "12345678", f"admin{i}@test.com")
            for i in range(10)
        ],
    },
    "test_get_users": {
        "argnames": "name, password1",
        "argvalues": [(f"admin{i}", "12345678") for i in range(10)],
    },
    "test_create_board": {
        "argnames": "admin_name, admin_password1, board_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "board_name": f"board_{i}_{j}",
                        "board_information": f"board_{i}_{j}_information",
                        "board_is_visible": True,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_create_user_for_update_user_board_permission": {
        "argnames": "name, password1, password2, email",
        "argvalues": [
            (f"user{i}", "12345678", "12345678", f"user{i}@test.com") for i in range(20)
        ],
    },
    "test_update_user_board_permission": {
        "argnames": "name, password1, test_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "user_id": f"{11+(i*2)+j}",
                        "board_id": f"{1+(i*2)+j}",
                        "user_is_permitted": True,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_update_user_is_banned": {
        "argnames": "name, password1, test_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "user_id": f"{11+(i*2)+j}",
                        "user_is_banned": True,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
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


class AdminTestMethods:
    def create_admin(self, name, password1, password2, email):
        input_iter = iter([name, email]).__next__
        getpass_iter = iter([password1, password2]).__next__

        monkeypatch = MonkeyPatch()
        monkeypatch.setattr("builtins.input", lambda _: input_iter())
        monkeypatch.setattr("getpass.getpass", lambda _: getpass_iter())

        create_admin_with_terminal(data_base=None)

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

    def get_users_test(self, response_test: Response):
        # get_users 후 진행

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        for user in response_test_json.get("users"):
            user: dict

            assert user.get("name") != None
            assert user.get("email") != None
            assert user.get("join_date") != None
            assert user.get("boards") != None
            assert user.get("posts") != None

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
        assert response_test.json() == {"result": "success"}

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

    @pytest.mark.parametrize(**test_parameter_dict["test_create_admin"])
    def test_create_admin(self, name, password1, password2, email):
        admin_test_methods.create_admin(name, password1, password2, email)
        admin_test_methods.create_admin_test(name, password1, email)

    @pytest.mark.parametrize(**test_parameter_dict["test_get_users"])
    def test_get_users(self, name, password1):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = admin_test_methods.get_users(access_token)
        admin_test_methods.get_users_test(response_test)

    @pytest.mark.parametrize(**test_parameter_dict["test_create_board"])
    def test_create_board(self, admin_name, admin_password1, board_args):
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

    @pytest.mark.parametrize(
        **test_parameter_dict["test_create_user_for_update_user_board_permission"]
    )
    def test_create_user_for_update_user_board_permission(
        self, name, password1, password2, email
    ):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        user_test_methods.create_user_test(
            response_test, name, password1, email
        )

    @pytest.mark.parametrize(**test_parameter_dict["test_update_user_board_permission"])
    def test_update_user_board_permission(self, name, password1, test_args):

        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for test_arg in test_args:

            response_test = admin_test_methods.update_user_board_permission(
                **test_arg, access_token=access_token
            )
            admin_test_methods.update_user_board_permission_test(
                **test_arg, response_test=response_test
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_update_user_is_banned"])
    def test_update_user_is_banned(self, name, password1, test_args):

        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for test_arg in test_args:

            response_test = admin_test_methods.update_user_is_banned(
                **test_arg, access_token=access_token
            )
            admin_test_methods.update_user_is_banned_test(
                **test_arg, response_test=response_test
            )

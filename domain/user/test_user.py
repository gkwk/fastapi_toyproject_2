import pytest
import json

from fastapi.testclient import TestClient
from httpx import Response

from main import app
from models import User
from database import session_local
from auth import validate_and_decode_user_access_token
import v1_urn
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
    "URL_USER_GET_USER_DETAIL": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.USER_PREFIX,
        v1_urn.USER_GET_USER_DETAIL,
    ],
    "URL_USER_UPDATE_USER_DETAIL": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.USER_PREFIX,
        v1_urn.USER_UPDATE_USER_DETAIL,
    ],
    "URL_USER_UPDATE_USER_PASSWORD": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.USER_PREFIX,
        v1_urn.USER_UPDATE_USER_PASSWORD,
    ],
}


URL_USER_CREATE_USER = "".join(url_dict.get("URL_USER_CREATE_USER"))
URL_USER_LOGIN_USER = "".join(url_dict.get("URL_USER_LOGIN_USER"))
URL_USER_GET_USER_DETAIL = "".join(url_dict.get("URL_USER_GET_USER_DETAIL"))
URL_USER_UPDATE_USER_DETAIL = "".join(url_dict.get("URL_USER_UPDATE_USER_DETAIL"))
URL_USER_UPDATE_USER_PASSWORD = "".join(url_dict.get("URL_USER_UPDATE_USER_PASSWORD"))


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


ID_DICT_USER_ID = "user_id"


id_list_dict = {ID_DICT_USER_ID: []}

id_iterator_dict = {ID_DICT_USER_ID: iter([])}


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


class UserTestMethods:
    def access_token_validate(self, access_token):
        data_base = session_local()

        user_payload = validate_and_decode_user_access_token(
            data_base=data_base, token=access_token
        )

        data_base.close()

        return user_payload

    def create_user(self, name, password1, password2, email):
        response_test = client.post(
            URL_USER_CREATE_USER,
            json={
                "name": name,
                "password1": password1,
                "password2": password2,
                "email": email,
            },
        )

        return response_test

    def create_user_test(self, response_test: Response, name, password1, email):
        data_base = session_local()
        assert response_test.status_code == 201

        response_test_json: dict = response_test.json()

        assert response_test_json.get("result") == "success"
        assert response_test_json.get("id") > 0

        user = data_base.query(User).filter_by(id=response_test_json.get("id")).first()

        assert user.name == name
        assert user.email == email
        assert user.password != password1
        assert user.password_salt != None
        assert user.join_date != None
        assert user.update_date == None
        assert user.is_superuser == False
        assert user.is_banned == False

        data_base.close()

    def login_user(self, name, password1):
        response_test = client.post(
            URL_USER_LOGIN_USER,
            data={"username": name, "password": password1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        return response_test

    def login_user_test(self, user_id, name, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 200
        response_test_json: dict = response_test.json()
        assert response_test_json.get("access_token")
        assert response_test_json.get("token_type") == "bearer"

        user_payload = self.access_token_validate(
            response_test_json.get("access_token")
        )

        assert user_payload.get("user_id") >= user_id
        assert user_payload.get("user_name") == name
        assert user_payload.get("is_admin") == False

        user = data_base.query(User).filter_by(id=user_id).first()

        assert user.name == name

        data_base.close()

    def get_user_detail(self, access_token: str):
        response_test = client.get(
            URL_USER_GET_USER_DETAIL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return response_test

    def get_user_detail_test(self, user_columns, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        assert set(user_columns) == set(response_test_json.keys())

        data_base.close()

    def update_user_detail(self, email_update, access_token: str):
        response_test = client.put(
            URL_USER_UPDATE_USER_DETAIL,
            json={
                "email": email_update,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def update_user_detail_test(self, user_id, email_update, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 204

        user = data_base.query(User).filter_by(id=user_id).first()

        assert user.email == email_update
        assert user.update_date != None

        data_base.close()

    def update_user_password(
        self, user_id, password1_update, password2_update, access_token: str
    ):
        data_base = session_local()
        user = data_base.query(User).filter_by(id=user_id).first()
        user_password_salt_old = user.password_salt

        response_test = client.put(
            URL_USER_UPDATE_USER_PASSWORD,
            json={
                "password1": password1_update,
                "password2": password2_update,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        data_base.close()

        return {
            "response_test": response_test,
            "user_password_salt_old": user_password_salt_old,
        }

    def update_user_password_test(
        self,
        user_id,
        name,
        user_password_salt_old,
        response_test: Response,
    ):
        data_base = session_local()

        assert response_test.status_code == 204

        user = data_base.query(User).filter_by(id=user_id).first()

        user_password_salt_new = user.password_salt

        assert user.name == name
        assert user.password_salt != None
        assert user_password_salt_new != user_password_salt_old
        assert user.update_date != None

        data_base.close()


user_test_methods = UserTestMethods()


class TestUser:
    def test_data_base_init(self):
        main_test_methods.data_base_init()

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/user/test_create_user.json")
    )
    def test_create_user(self, pn, name, password1, password2, email):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        user_test_methods.create_user_test(response_test, name, password1, email)

        id_list_append(ID_DICT_USER_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/user/test_login_user.json")
    )
    def test_login_user(self, pn, name, password1):
        user_id = id_iterator_next(pn, ID_DICT_USER_ID)

        response_test = user_test_methods.login_user(name, password1)

        user_test_methods.login_user_test(user_id, name, response_test)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/user/test_get_user_detail.json")
    )
    def test_get_user_detail(self, pn, name, password1, user_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = user_test_methods.get_user_detail(access_token)
        user_test_methods.get_user_detail_test(user_columns, response_test)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/user/test_update_user_detail.json")
    )
    def test_update_user_detail(self, pn, name, password1, email_update):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")
        user_id = id_iterator_next(pn, ID_DICT_USER_ID)

        response_test = user_test_methods.update_user_detail(email_update, access_token)
        user_test_methods.update_user_detail_test(user_id, email_update, response_test)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/user/test_update_user_password.json")
    )
    def test_update_user_password(
        self, pn, name, password1, password1_update, password2_update
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")
        user_id = id_iterator_next(pn, ID_DICT_USER_ID)

        response_dict = user_test_methods.update_user_password(
            user_id, password1_update, password2_update, access_token
        )

        user_test_methods.update_user_password_test(user_id, name, **response_dict)

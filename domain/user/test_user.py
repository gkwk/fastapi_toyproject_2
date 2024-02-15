import pytest

from fastapi.testclient import TestClient
from httpx import Response

from main import app
from models import User
from database import session_local
from auth import validate_and_decode_user_access_token
import v1_urn
from test_main import main_test_methods

client = TestClient(app)

TEST_USER_ID = "user"
TEST_USER_EMAIL = "user@test.com"
TEST_USER_PASSWORD1 = "12345678"
TEST_USER_PASSWORD2 = "12345678"

TEST_USER_EMAIL_UPDATE = "user_update@test.com"
TEST_USER_PASSWORD1_UPDATE = "123456789"
TEST_USER_PASSWORD2_UPDATE = "123456789"

URL_USER_CREATE_USER = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.USER_PREFIX, v1_urn.USER_CREATE_USER]
)
URL_USER_LOGIN_USER = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.USER_PREFIX, v1_urn.USER_LOGIN_USER]
)
URL_USER_GET_USER_DETAIL = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.USER_PREFIX, v1_urn.USER_GET_USER_DETAIL]
)
URL_USER_UPDATE_USER_DETAIL = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.USER_PREFIX, v1_urn.USER_UPDATE_USER_DETAIL]
)
URL_USER_UPDATE_USER_PASSWORD = "".join(
    [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.USER_PREFIX, v1_urn.USER_UPDATE_USER_PASSWORD]
)


class UserTestMethods:
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
        assert response_test.json() == {"result": "success"}

        user = data_base.query(User).filter_by(name=name, email=email).first()

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

    def login_user_test(self, response_test: Response, name):
        data_base = session_local()

        assert response_test.status_code == 200
        response_test_json: dict = response_test.json()
        assert response_test_json.get("access_token")
        assert response_test_json.get("token_type") == "bearer"

        user_payload = validate_and_decode_user_access_token(
            data_base=data_base, token=response_test_json.get("access_token")
        )

        assert user_payload.get("user_id") >= 1
        assert user_payload.get("user_name") == name
        assert user_payload.get("is_admin") == False

        user = data_base.query(User).filter_by(id=user_payload.get("user_id")).first()

        assert user.name == name

        data_base.close()

    def get_user_detail(self, name, password1):
        response_login: Response = self.login_user(name, password1)
        response_login_json: dict = response_login.json()

        response_test = client.get(
            URL_USER_GET_USER_DETAIL,
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )
        return response_test

    def get_user_detail_test(self, response_test: Response, name, email):
        data_base = session_local()

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        assert response_test_json.get("name") == name
        assert response_test_json.get("email") == email
        assert response_test_json.get("join_date") != None
        assert response_test_json.get("boards") != None
        assert response_test_json.get("posts") != None

        data_base.close()

    def update_user_detail(self, name, password1, email_update):
        response_login: Response = self.login_user(name, password1)
        response_login_json: dict = response_login.json()

        response_test = client.put(
            URL_USER_UPDATE_USER_DETAIL,
            json={
                "email": email_update,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        return response_test

    def update_user_detail_test(self, response_test: Response, name, email_update):
        data_base = session_local()

        assert response_test.status_code == 204

        user = data_base.query(User).filter_by(name=name).first()

        assert user.email == email_update
        assert user.update_date != None

        data_base.close()

    def update_user_password(self, name, password1, password1_update, password2_update):
        data_base = session_local()

        response_login: Response = self.login_user(name, password1)
        response_login_json: dict = response_login.json()

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=response_login_json.get("access_token")
        ).get("user_id")

        user = data_base.query(User).filter_by(id=user_id).first()
        user_password_salt_old = user.password_salt

        response_test = client.put(
            URL_USER_UPDATE_USER_PASSWORD,
            json={
                "password1": password1_update,
                "password2": password2_update,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        data_base.close()

        return {
            "response_test": response_test,
            "user_password_salt_old": user_password_salt_old,
            "user_id": user_id,
        }

    def update_user_password_test(
        self,
        name,
        password1_update,
        response_test: Response,
        user_password_salt_old,
        user_id,
    ):
        data_base = session_local()

        assert response_test.status_code == 204

        response_login: Response = self.login_user(name, password1_update)
        response_login_json: dict = response_login.json()

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=response_login_json.get("access_token")
        ).get("user_id")

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
        "name, password1, password2, email",
        [(f"user{i}", "12345678", "12345678", f"user{i}@test.com") for i in range(10)],
    )
    def test_create_user(self, name, password1, password2, email):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        user_test_methods.create_user_test(response_test, name, password1, email)

    @pytest.mark.parametrize(
        "name, password1",
        [(f"user{i}", "12345678") for i in range(10)],
    )
    def test_login_user(self, name, password1):
        response_test = user_test_methods.login_user(name, password1)
        user_test_methods.login_user_test(response_test, name)

    @pytest.mark.parametrize(
        "name, password1, email",
        [(f"user{i}", "12345678", f"user{i}@test.com") for i in range(10)],
    )
    def test_get_user_detail(self, name, password1, email):
        response_test = user_test_methods.get_user_detail(name, password1)
        user_test_methods.get_user_detail_test(response_test, name, email)

    @pytest.mark.parametrize(
        "name, password1, email_update",
        [(f"user{i}", "12345678", f"user{i}_update@test.com") for i in range(10)],
    )
    def test_update_user_detail(self, name, password1, email_update):
        response_test = user_test_methods.update_user_detail(
            name, password1, email_update
        )
        user_test_methods.update_user_detail_test(response_test, name, email_update)

    @pytest.mark.parametrize(
        " name, password1, password1_update, password2_update",
        [(f"user{i}", "12345678", "12345679", "12345679") for i in range(10)],
    )
    def test_update_user_password(
        self, name, password1, password1_update, password2_update
    ):
        response_dict = user_test_methods.update_user_password(
            name, password1, password1_update, password2_update
        )
        user_test_methods.update_user_password_test(
            name, password1_update, **response_dict
        )

from fastapi.testclient import TestClient

from main import app
from models import User
from database import session_local
from auth import validate_and_decode_user_access_token
import v1_urn

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


class TestUser:
    def test_data_base_init(self):
        data_base = session_local()
        data_base.query(User).delete()
        data_base.commit()
        data_base.close()

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
        assert user.update_date == None
        assert user.is_superuser == False
        assert user.is_banned == False

        data_base.close()

    def test_login_user(self):
        data_base = session_local()

        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_USER_ID, "password": TEST_USER_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type") == "bearer"

        user_payload = validate_and_decode_user_access_token(
            data_base=data_base, token=response_login_json.get("access_token")
        )

        assert user_payload.get("user_id") >= 1
        assert user_payload.get("user_name") == TEST_USER_ID
        assert user_payload.get("is_admin") == False

        data_base.close()

    def test_get_user_detail(self):
        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_USER_ID, "password": TEST_USER_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        response_test = client.get(
            URL_USER_GET_USER_DETAIL,
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        assert response_test_json.get("name") == TEST_USER_ID
        assert response_test_json.get("email") == TEST_USER_EMAIL
        assert response_test_json.get("join_date") != None
        assert response_test_json.get("boards") != None
        assert response_test_json.get("posts") != None

    def test_update_user_detail(self):
        data_base = session_local()

        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_USER_ID, "password": TEST_USER_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=response_login_json.get("access_token")
        ).get("user_id")
        user = data_base.query(User).filter_by(id=user_id).first()

        response_test = client.put(
            URL_USER_UPDATE_USER_DETAIL,
            json={
                "email": TEST_USER_EMAIL_UPDATE,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
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

        data_base.close()

    def test_update_user_password(self):
        data_base = session_local()

        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_USER_ID, "password": TEST_USER_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=response_login_json.get("access_token")
        ).get("user_id")

        user = data_base.query(User).filter_by(id=user_id).first()
        user_password_salt_old = user.password_salt

        response_test = client.put(
            URL_USER_UPDATE_USER_PASSWORD,
            json={
                "password1": TEST_USER_PASSWORD1_UPDATE,
                "password2": TEST_USER_PASSWORD2_UPDATE,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )
        data_base.commit()

        assert response_test.status_code == 204

        response_login = client.post(
            URL_USER_LOGIN_USER,
            data={"username": TEST_USER_ID, "password": TEST_USER_PASSWORD1_UPDATE},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=response_login_json.get("access_token")
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

        data_base.close()

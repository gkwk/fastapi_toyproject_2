from pytest import MonkeyPatch
import pytest
import time

from fastapi.testclient import TestClient
from httpx import Response


from celery.result import AsyncResult

from main import app
from models import User, AI, AIlog
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
    "URL_AI_TRAIN_AI": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.AI_PREFIX,
        v1_urn.AI_TRAIN_AI,
    ],
    "URL_AI_GET_AI": [v1_urn.API_V1_ROUTER_PREFIX, v1_urn.AI_PREFIX, v1_urn.AI_GET_AI],
    "URL_AI_GET_AIS": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.AI_PREFIX,
        v1_urn.AI_GET_AIS,
    ],
    "URL_AI_UPDATE_AI": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.AI_PREFIX,
        v1_urn.AI_UPDATE_AI,
    ],
    "URL_AI_DELETE_AI": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.AI_PREFIX,
        v1_urn.AI_DELETE_AI,
    ],
    "URL_AI_AI_INFER": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.AI_PREFIX,
        v1_urn.AI_AI_INFER,
    ],
    "URL_AI_GET_AILOG": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.AI_PREFIX,
        v1_urn.AI_GET_AILOG,
    ],
    "URL_AI_GET_AILOGS": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.AI_PREFIX,
        v1_urn.AI_GET_AILOGS,
    ],
    "URL_AI_UPDATE_AILOG": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.AI_PREFIX,
        v1_urn.AI_UPDATE_AILOG,
    ],
    "URL_AI_DELETE_AILOG": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.AI_PREFIX,
        v1_urn.AI_DELETE_AILOG,
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
    "test_train_ai": {
        "argnames": "name, password1, ai_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "ai_name": f"admin{i}_{j}_ai",
                        "ai_description": f"admin{i}_{j}_ai_description",
                        "ai_is_visible": True,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_get_ai": {
        "argnames": "name, password1, ai_args1, ai_args2",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "ai_id": f"{1+(i*2)+j}",
                    }
                    for j in range(2)
                ],
                [
                    {
                        "ai_name": f"admin{i}_{j}_ai",
                        "ai_description": f"admin{i}_{j}_ai_description",
                        "ai_is_visible": True,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_get_ais": {
        "argnames": "name, password1, ais_params, ai_columns",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                {
                    "ai_is_available": True,
                    "ai_is_visible": True,
                    "ai_skip": None,
                    "ai_limit": 100,
                },
                [
                    "id",
                    "is_available",
                    "name",
                    "is_visible",
                    "description",
                    "create_date",
                    "finish_date",
                    "update_date",
                    "celery_task_id",
                ],
            )
            for i in range(10)
        ],
    },
    "test_update_ai": {
        "argnames": "name, password1, ai_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "ai_id": j,
                        "ai_description_update": f"{j}_admin{i}_description_update",
                        "ai_is_visible_update": False,
                        "ai_is_available_update": False,
                    }
                    for j in range(1, 20 + 1)
                ],
            )
            for i in range(10)
        ],
    },
    "test_delete_ai": {
        "argnames": "name, password1, ai_id_list",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [1 + (i * 2) + j for j in range(2)],
            )
            for i in range(10)
        ],
    },
    "test_ai_infer": {
        "argnames": "name, password1, ai_id_list, ailog_description_list",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [1 + (i * 2) + j for j in range(2)],
                [
                    f"AIlog_test_admin{i}_ai_{1 + (i * 2) + j}_description"
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_get_ailog": {
        "argnames": "name, password1, ailog_ids, ailog_columns",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [1 + (i * 2) + j for j in range(2)],
                [
                    "user_id",
                    "ai_id",
                    "description",
                    "create_date",
                    "result",
                    "is_finished",
                    "update_date",
                    "celery_task_id",
                ],
            )
            for i in range(10)
        ],
    },
    "test_get_ailogs": {
        "argnames": "name, password1, ailogs_params, ailog_columns",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                {
                    "user_id": None,
                    "ai_id": None,
                    "ailog_skip": None,
                    "ailog_limit": 100,
                },
                [
                    "user_id",
                    "ai_id",
                    "description",
                    "create_date",
                    "result",
                    "is_finished",
                    "update_date",
                    "celery_task_id",
                ],
            )
            for i in range(10)
        ],
    },
    "test_update_ailog": {
        "argnames": "name, password1, ailog_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "ailog_id": 1 + (i * 2) + j,
                        "ailog_description_update": f"{1 + (i * 2) + j}_admin{i}_description_update",
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_delete_ailog": {
        "argnames": "name, password1, ailog_id_list",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [1 + (i * 2) + j for j in range(2)],
            )
            for i in range(10)
        ],
    },
}

URL_USER_CREATE_USER = "".join(url_dict.get("URL_USER_CREATE_USER"))
URL_USER_LOGIN_USER = "".join(url_dict.get("URL_USER_LOGIN_USER"))
URL_AI_TRAIN_AI = "".join(url_dict.get("URL_AI_TRAIN_AI"))
URL_AI_GET_AI = "".join(url_dict.get("URL_AI_GET_AI"))
URL_AI_GET_AIS = "".join(url_dict.get("URL_AI_GET_AIS"))
URL_AI_UPDATE_AI = "".join(url_dict.get("URL_AI_UPDATE_AI"))
URL_AI_DELETE_AI = "".join(url_dict.get("URL_AI_DELETE_AI"))
URL_AI_AI_INFER = "".join(url_dict.get("URL_AI_AI_INFER"))
URL_AI_GET_AILOG = "".join(url_dict.get("URL_AI_GET_AILOG"))
URL_AI_GET_AILOGS = "".join(url_dict.get("URL_AI_GET_AILOGS"))
URL_AI_UPDATE_AILOG = "".join(url_dict.get("URL_AI_UPDATE_AILOG"))
URL_AI_DELETE_AILOG = "".join(url_dict.get("URL_AI_DELETE_AILOG"))


class AITestMethods:
    def train_ai(self, ai_name, ai_description, ai_is_visible, access_token: str):
        response_test = client.post(
            URL_AI_TRAIN_AI,
            json={
                "name": ai_name,
                "description": ai_description,
                "is_visible": ai_is_visible,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def train_ai_test(
        self, ai_name, ai_description, ai_is_visible, response_test: Response
    ):
        data_base = session_local()
        assert response_test.status_code == 201
        response_test_json: dict = response_test.json()
        assert response_test_json.get("task_id")

        task_result = AsyncResult(response_test_json.get("task_id"))

        while task_result.state == "PENDING":
            time.sleep(0.5)

        ai = (
            data_base.query(AI)
            .filter_by(celery_task_id=response_test_json.get("task_id"))
            .first()
        )

        assert ai.is_available == True
        assert ai.name == ai_name
        assert ai.is_visible == ai_is_visible
        assert ai.description == ai_description
        assert ai.finish_date != None
        assert ai.update_date != None
        assert ai.create_date != None
        assert ai.celery_task_id == response_test_json.get("task_id")

        data_base.close()

    def get_ai(self, ai_id, access_token: str):
        response_test = client.get(
            URL_AI_GET_AI,
            params={
                "ai_id": ai_id,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def get_ai_test(
        self, ai_name, ai_description, ai_is_visible, response_test: Response
    ):
        data_base = session_local()

        assert response_test.status_code == 200
        response_test_json: dict = response_test.json()

        assert response_test_json.get("is_available") == True
        assert response_test_json.get("name") == ai_name
        assert response_test_json.get("is_visible") == ai_is_visible
        assert response_test_json.get("description") == ai_description
        assert response_test_json.get("create_date") != None

        if response_test_json.get("is_available"):
            assert response_test_json.get("finish_date") != None
            assert response_test_json.get("update_date") != None
        else:
            assert response_test_json.get("finish_date") == None
            assert response_test_json.get("update_date") == None

        assert response_test_json.get("celery_task_id") != None

        data_base.close()

    def get_ais(
        self, ai_is_available, ai_is_visible, ai_skip, ai_limit, access_token: str
    ):
        params = {}
        if ai_is_available != None:
            params["is_available"] = ai_is_available
        if ai_is_visible != None:
            params["is_visible"] = ai_is_visible
        if ai_skip != None:
            params["skip"] = ai_skip
        if ai_limit != None:
            params["limit"] = ai_limit

        response_test = client.get(
            URL_AI_GET_AIS,
            params=params,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def get_ais_test(self, ai_columns, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 200
        response_test_json: dict = response_test.json()

        assert response_test_json.get("total") >= 0

        for ai in response_test_json.get("ais"):
            ai: dict

            for column in ai_columns:
                assert column in ai
        data_base.close()

    def update_ai(
        self,
        ai_id,
        ai_description_update,
        ai_is_visible_update,
        ai_is_available_update,
        access_token: str,
    ):
        response_test = client.put(
            URL_AI_UPDATE_AI,
            json={
                "ai_id": ai_id,
                "description": ai_description_update,
                "is_visible": ai_is_visible_update,
                "is_available": ai_is_available_update,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def update_ai_test(
        self,
        ai_id,
        ai_description_update,
        ai_is_visible_update,
        ai_is_available_update,
        response_test: Response,
    ):
        data_base = session_local()

        ai = data_base.query(AI).filter_by(id=ai_id).first()

        assert response_test.status_code == 204

        assert ai.is_available == ai_is_available_update
        assert ai.is_visible == ai_is_visible_update
        assert ai.description == ai_description_update
        assert ai.update_date != None

        data_base.close()

    def delete_ai(self, ai_id, access_token: str):
        response_test = client.delete(
            URL_AI_DELETE_AI,
            params={
                "ai_id": ai_id,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def delete_ai_test(self, ai_id, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 204

        ai = data_base.query(AI).filter_by(id=ai_id).first()

        assert ai == None

        data_base.close()


class AIlogTestMethods:
    def ai_infer(self, ai_id, ailog_description, access_token: str):
        response_test = client.post(
            URL_AI_AI_INFER,
            json={
                "ai_id": ai_id,
                "description": ailog_description,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def ai_infer_test(
        self, ai_id, ailog_description, access_token: str, response_test: Response
    ):
        data_base = session_local()

        assert response_test.status_code == 201
        response_test_json: dict = response_test.json()
        assert response_test_json.get("task_id")

        task_result = AsyncResult(response_test_json.get("task_id"))

        while task_result.state == "PENDING":
            time.sleep(0.5)

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=access_token
        ).get("user_id")

        ailogs = (
            data_base.query(AIlog)
            .filter_by(celery_task_id=response_test_json.get("task_id"))
            .first()
        )

        assert ailogs.user_id == user_id
        assert ailogs.ai_id == ai_id
        assert ailogs.description == ailog_description
        assert ailogs.finish_date != None
        assert ailogs.update_date != None
        assert ailogs.create_date != None
        assert ailogs.result != None
        assert ailogs.is_finished != None
        assert ailogs.celery_task_id == response_test_json.get("task_id")

        data_base.close()

    def get_ailog(self, ailog_id, access_token: str):
        response_test = client.get(
            URL_AI_GET_AILOG,
            params={"ailog_id": ailog_id},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def get_ailog_test(self, ailog_columns, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 200
        response_test_json: dict = response_test.json()

        for ailog_column in ailog_columns:
            assert ailog_column in response_test_json
        data_base.close()

    def get_ailogs(self, user_id, ai_id, ailog_skip, ailog_limit, access_token: str):
        params = {}
        if user_id != None:
            params["user_id"] = user_id
        if ai_id != None:
            params["ai_id"] = ai_id
        if ailog_skip != None:
            params["skip"] = ailog_skip
        if ailog_limit != None:
            params["limit"] = ailog_limit

        response_test = client.get(
            URL_AI_GET_AILOGS,
            params=params,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def get_ailogs_test(self, ailog_columns, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 200
        response_test_json: dict = response_test.json()

        assert response_test_json.get("total") >= 0

        for ailog in response_test_json.get("ailogs"):
            ailog: dict

            for ailog_column in ailog_columns:
                assert ailog_column in ailog
        data_base.close()

    def update_ailog(self, ailog_id, ailog_description_update, access_token: str):
        response_test = client.put(
            URL_AI_UPDATE_AILOG,
            json={
                "ailog_id": ailog_id,
                "description": ailog_description_update,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def update_ailog_test(
        self, ailog_id, ailog_description_update, response_test: Response
    ):
        data_base = session_local()

        assert response_test.status_code == 204
        ailog = data_base.query(AIlog).filter_by(id=ailog_id).first()

        assert ailog.description == ailog_description_update
        assert ailog.update_date != None

        data_base.close()

    def delete_ailog(self, ailog_id, access_token: str):
        response_test = client.delete(
            URL_AI_DELETE_AILOG,
            params={
                "ailog_id": ailog_id,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def delete_ailog_test(self, ailog_id, response_test: Response):
        data_base = session_local()
        assert response_test.status_code == 204

        ailog = data_base.query(AIlog).filter_by(id=ailog_id).first()

        assert ailog == None
        data_base.close()


ai_test_methods = AITestMethods()
ailog_test_methods = AIlogTestMethods()


class TestAI:
    def test_data_base_init(self):
        main_test_methods.data_base_init()

    @pytest.mark.parametrize(**test_parameter_dict["test_create_admin"])
    def test_create_admin(self, name, password1, password2, email):
        admin_test_methods.create_admin(name, password1, password2, email)
        admin_test_methods.create_admin_test(name, password1, email)

    @pytest.mark.parametrize(**test_parameter_dict["test_create_user"])
    def test_create_user(self, name, password1, password2, email):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        user_test_methods.create_user_test_success(
            response_test, name, password1, email
        )

    @pytest.mark.parametrize(**test_parameter_dict["test_train_ai"])
    def test_train_ai(
        self,
        celery_app,
        celery_worker,
        name,
        password1,
        ai_args,
    ):
        celery_worker.reload()

        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for ai_arg in ai_args:
            response_test = ai_test_methods.train_ai(
                **ai_arg, access_token=access_token
            )
            ai_test_methods.train_ai_test(**ai_arg, response_test=response_test)

    @pytest.mark.parametrize(**test_parameter_dict["test_get_ai"])
    def test_get_ai(
        self,
        name,
        password1,
        ai_args1,
        ai_args2,
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for ai_arg1, ai_arg2 in zip(ai_args1, ai_args2):
            response_test = ai_test_methods.get_ai(**ai_arg1, access_token=access_token)
            ai_test_methods.get_ai_test(**ai_arg2, response_test=response_test)

    @pytest.mark.parametrize(**test_parameter_dict["test_get_ais"])
    def test_get_ais(
        self,
        name,
        password1,
        ais_params,
        ai_columns,
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = ai_test_methods.get_ais(**ais_params, access_token=access_token)
        ai_test_methods.get_ais_test(ai_columns, response_test=response_test)

    @pytest.mark.parametrize(**test_parameter_dict["test_update_ai"])
    def test_update_ai(
        self,
        name,
        password1,
        ai_args,
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for ai_arg in ai_args:
            response_test = ai_test_methods.update_ai(
                **ai_arg, access_token=access_token
            )
            ai_test_methods.update_ai_test(**ai_arg, response_test=response_test)

    @pytest.mark.parametrize(**test_parameter_dict["test_delete_ai"])
    def test_delete_ai(self, name, password1, ai_id_list):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for ai_id in ai_id_list:
            response_test = ai_test_methods.delete_ai(ai_id, access_token=access_token)
            ai_test_methods.delete_ai_test(ai_id, response_test=response_test)


class TestAIlog:
    def test_data_base_init(self):
        main_test_methods.data_base_init()

    @pytest.mark.parametrize(**test_parameter_dict["test_create_admin"])
    def test_create_admin(self, name, password1, password2, email):
        admin_test_methods.create_admin(name, password1, password2, email)
        admin_test_methods.create_admin_test(name, password1, email)

    @pytest.mark.parametrize(**test_parameter_dict["test_create_user"])
    def test_create_user(self, name, password1, password2, email):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        user_test_methods.create_user_test_success(
            response_test, name, password1, email
        )

    @pytest.mark.parametrize(**test_parameter_dict["test_train_ai"])
    def test_train_ai(
        self,
        celery_app,
        celery_worker,
        name,
        password1,
        ai_args,
    ):
        celery_worker.reload()

        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for ai_arg in ai_args:
            response_test = ai_test_methods.train_ai(
                **ai_arg, access_token=access_token
            )
            ai_test_methods.train_ai_test(**ai_arg, response_test=response_test)

    @pytest.mark.parametrize(**test_parameter_dict["test_ai_infer"])
    def test_ai_infer(
        self,
        celery_app,
        celery_worker,
        name,
        password1,
        ai_id_list,
        ailog_description_list,
    ):
        celery_worker.reload()

        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for ai_id, ailog_description in zip(ai_id_list, ailog_description_list):
            response_test = ailog_test_methods.ai_infer(
                ai_id, ailog_description, access_token=access_token
            )
            ailog_test_methods.ai_infer_test(
                ai_id, ailog_description, access_token, response_test=response_test
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_get_ailog"])
    def test_get_ailog(self, name, password1, ailog_ids, ailog_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for ailog_id in ailog_ids:
            response_test = ailog_test_methods.get_ailog(
                ailog_id, access_token=access_token
            )
            ailog_test_methods.get_ailog_test(
                ailog_columns, response_test=response_test
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_get_ailogs"])
    def test_get_ailogs(self, name, password1, ailogs_params, ailog_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = ailog_test_methods.get_ailogs(
            **ailogs_params, access_token=access_token
        )
        ailog_test_methods.get_ailogs_test(ailog_columns, response_test=response_test)

    @pytest.mark.parametrize(**test_parameter_dict["test_update_ailog"])
    def test_update_ailog(
        self,
        name,
        password1,
        ailog_args,
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for ailog_arg in ailog_args:
            response_test = ailog_test_methods.update_ailog(
                **ailog_arg, access_token=access_token
            )
            ailog_test_methods.update_ailog_test(
                **ailog_arg, response_test=response_test
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_delete_ailog"])
    def test_delete_ailog(self, name, password1, ailog_id_list):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for ailog_id in ailog_id_list:
            response_test = ailog_test_methods.delete_ailog(
                ailog_id, access_token=access_token
            )
            ailog_test_methods.delete_ailog_test(ailog_id, response_test=response_test)

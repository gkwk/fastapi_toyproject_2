from pytest import MonkeyPatch
import pytest
import time
import json

from fastapi.testclient import TestClient
from httpx import Response

from celery.result import AsyncResult

from main import app
from models import AI, AIlog
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
ID_DICT_AI_ID = "ai_id"
ID_DICT_AILOG_ID = "ailog_id"

id_list_dict = {
    ID_DICT_ADMIN_ID: [],
    ID_DICT_USER_ID: [],
    ID_DICT_AI_ID: [],
    ID_DICT_AILOG_ID: [],
}

id_iterator_dict = {
    ID_DICT_ADMIN_ID: iter([]),
    ID_DICT_USER_ID: iter([]),
    ID_DICT_AI_ID: iter([]),
    ID_DICT_AILOG_ID: iter([]),
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
        assert response_test_json.get("id") > 0

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

    def get_ai_test(self, ai_columns, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 200
        response_test_json: dict = response_test.json()

        assert set(ai_columns) == set(response_test_json.keys())

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
            assert set(ai_columns) == set(ai.keys())
        data_base.close()

    def update_ai(
        self,
        *,
        ai_id,
        ai_description_update=None,
        ai_is_visible_update=None,
        ai_is_available_update=None,
        access_token: str,
    ):
        params = {}
        if ai_description_update != None:
            params["description"] = ai_description_update
        if ai_is_visible_update != None:
            params["is_visible"] = ai_is_visible_update
        if ai_is_available_update != None:
            params["is_available"] = ai_is_available_update

        response_test = client.put(
            URL_AI_UPDATE_AI,
            json={"ai_id": ai_id, **params},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def update_ai_test(
        self,
        *,
        ai_id,
        ai_description_update=None,
        ai_is_visible_update=None,
        ai_is_available_update=None,
        response_test: Response,
    ):
        data_base = session_local()

        ai = data_base.query(AI).filter_by(id=ai_id).first()

        assert response_test.status_code == 204

        if ai_is_available_update != None:
            assert ai.is_available == ai_is_available_update
        if ai_is_visible_update != None:
            assert ai.is_visible == ai_is_visible_update
        if ai_description_update != None:
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
        assert response_test_json.get("id") > 0

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

        assert set(ailog_columns) == set(response_test_json.keys())
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
            assert set(ailog_columns) == set(ailog.keys())

        data_base.close()

    def update_ailog(
        self, *, ailog_id, ailog_description_update=None, access_token: str
    ):
        params = {}
        if ailog_description_update != None:
            params["description"] = ailog_description_update

        response_test = client.put(
            URL_AI_UPDATE_AILOG,
            json={"ailog_id": ailog_id, **params},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def update_ailog_test(
        self, *, ailog_id, ailog_description_update=None, response_test: Response
    ):
        data_base = session_local()

        assert response_test.status_code == 204
        ailog = data_base.query(AIlog).filter_by(id=ailog_id).first()

        if ailog_description_update != None:
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

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/ai/test_create_admin.json")
    )
    def test_create_admin(self, pn, name, password1, password2, email):
        admin_id = admin_test_methods.create_admin(name, password1, password2, email)
        id_list_append(ID_DICT_ADMIN_ID, admin_id)

    @pytest.mark.parametrize(**parameter_data_loader("domain/ai/test_create_user.json"))
    def test_create_user(self, pn, name, password1, password2, email):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        id_list_append(ID_DICT_USER_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(**parameter_data_loader("domain/ai/test_train_ai.json"))
    def test_train_ai(
        self,
        celery_app,
        celery_worker,
        pn,
        name,
        password1,
        ai_arg,
    ):
        celery_worker.reload()

        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = ai_test_methods.train_ai(**ai_arg, access_token=access_token)
        ai_test_methods.train_ai_test(**ai_arg, response_test=response_test)

        id_list_append(ID_DICT_AI_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(**parameter_data_loader("domain/ai/test_get_ai.json"))
    def test_get_ai(self, pn, name, password1, ai_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        ai_id = id_iterator_next(pn, ID_DICT_AI_ID)
        ai_id = ai_id if ai_id else 1

        response_test = ai_test_methods.get_ai(ai_id=ai_id, access_token=access_token)
        ai_test_methods.get_ai_test(ai_columns, response_test=response_test)

    @pytest.mark.parametrize(**parameter_data_loader("domain/ai/test_get_ais.json"))
    def test_get_ais(
        self,
        pn,
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

    @pytest.mark.parametrize(**parameter_data_loader("domain/ai/test_update_ai.json"))
    def test_update_ai(
        self,
        pn,
        name,
        password1,
        ai_arg,
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        ai_id = id_iterator_next(pn, ID_DICT_AI_ID)
        ai_id = ai_id if ai_id else 1

        response_test = ai_test_methods.update_ai(
            ai_id=ai_id, **ai_arg, access_token=access_token
        )
        ai_test_methods.update_ai_test(
            ai_id=ai_id, **ai_arg, response_test=response_test
        )

    @pytest.mark.parametrize(**parameter_data_loader("domain/ai/test_delete_ai.json"))
    def test_delete_ai(self, pn, name, password1, ai_id):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = ai_test_methods.delete_ai(ai_id, access_token=access_token)
        ai_test_methods.delete_ai_test(ai_id, response_test=response_test)


class TestAIlog:
    def test_data_base_init(self):
        main_test_methods.data_base_init()

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/ai/test_create_admin.json")
    )
    def test_create_admin(self, pn, name, password1, password2, email):
        admin_id = admin_test_methods.create_admin(name, password1, password2, email)
        id_list_append(ID_DICT_ADMIN_ID, admin_id)

    @pytest.mark.parametrize(**parameter_data_loader("domain/ai/test_create_user.json"))
    def test_create_user(self, pn, name, password1, password2, email):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        id_list_append(ID_DICT_USER_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(**parameter_data_loader("domain/ai/test_train_ai.json"))
    def test_train_ai(
        self,
        celery_app,
        celery_worker,
        pn,
        name,
        password1,
        ai_arg,
    ):
        celery_worker.reload()

        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = ai_test_methods.train_ai(**ai_arg, access_token=access_token)
        ai_test_methods.train_ai_test(**ai_arg, response_test=response_test)

        id_list_append(ID_DICT_AI_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(**parameter_data_loader("domain/ai/test_ai_infer.json"))
    def test_ai_infer(
        self,
        celery_app,
        celery_worker,
        pn,
        name,
        password1,
        ailog_description,
    ):
        celery_worker.reload()

        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        ai_id = id_iterator_next(pn, ID_DICT_AI_ID)
        ai_id = ai_id if ai_id else 1

        response_test = ailog_test_methods.ai_infer(
            ai_id, ailog_description, access_token=access_token
        )
        ailog_test_methods.ai_infer_test(
            ai_id, ailog_description, access_token, response_test=response_test
        )

        id_list_append(ID_DICT_AILOG_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(**parameter_data_loader("domain/ai/test_get_ailog.json"))
    def test_get_ailog(self, pn, name, password1, ailog_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        ailog_id = id_iterator_next(pn, ID_DICT_AILOG_ID)
        ailog_id = ailog_id if ailog_id else 1

        response_test = ailog_test_methods.get_ailog(
            ailog_id, access_token=access_token
        )
        ailog_test_methods.get_ailog_test(ailog_columns, response_test=response_test)

    @pytest.mark.parametrize(**parameter_data_loader("domain/ai/test_get_ailogs.json"))
    def test_get_ailogs(self, pn, name, password1, ailogs_params, ailog_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = ailog_test_methods.get_ailogs(
            **ailogs_params, access_token=access_token
        )
        ailog_test_methods.get_ailogs_test(ailog_columns, response_test=response_test)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/ai/test_update_ailog.json")
    )
    def test_update_ailog(
        self,
        pn,
        name,
        password1,
        ailog_arg,
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        ailog_id = id_iterator_next(pn, ID_DICT_AILOG_ID)
        ailog_id = ailog_id if ailog_id else 1

        response_test = ailog_test_methods.update_ailog(
            ailog_id=ailog_id, **ailog_arg, access_token=access_token
        )
        ailog_test_methods.update_ailog_test(
            ailog_id=ailog_id, **ailog_arg, response_test=response_test
        )

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/ai/test_delete_ailog.json")
    )
    def test_delete_ailog(self, pn, name, password1, ailog_id):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = ailog_test_methods.delete_ailog(
            ailog_id, access_token=access_token
        )
        ailog_test_methods.delete_ailog_test(ailog_id, response_test=response_test)

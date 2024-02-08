from pytest import MonkeyPatch
import time

from fastapi.testclient import TestClient

from celery.result import AsyncResult

from main import app
from domain.admin.admin_crud import create_admin_with_terminal
from models import User, AI, AIlog
from database import session_local, engine
from auth import validate_and_decode_user_access_token

client = TestClient(app)

TEST_ADMIN_ID = "admin"
TEST_ADMIN_EMAIL = "admin@test.com"
TEST_ADMIN_PASSWORD1 = "12345678"
TEST_ADMIN_PASSWORD2 = "12345678"

TEST_AI_NAME = "AI_test_1_name"
TEST_AI_DESCRIPTION = "AI_test_1_description"
TEST_AI_IS_VISIBLE = True

TEST_AI_DESCRIPTION_UPDATE = "AI_test_1_description_update"
TEST_AI_IS_VISIBLE_UPDATE = True
TEST_AI_IS_AVAILABLE_UPDATE = True

TEST_AI_LOG_DESCRIPTION = "AIlog_test_1_description"
TEST_AI_LOG_DESCRIPTION_UPDATE = "AIlog_test_1_description_update"


class TestAI:
    def test_data_base_init(self):
        data_base = session_local()
        data_base.query(AI).delete()
        data_base.query(AIlog).delete()
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

    def test_train_ai(self, celery_app, celery_worker):
        celery_worker.reload()
        data_base = session_local()

        response_admin_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_admin_login.status_code == 200
        response_admin_login_json: dict = response_admin_login.json()
        assert response_admin_login_json.get("access_token")
        assert response_admin_login_json.get("token_type")

        response_train_ai = client.post(
            "/api/v1/ai/train_ai",
            json={
                "name": TEST_AI_NAME,
                "description": TEST_AI_DESCRIPTION,
                "is_visible": TEST_AI_IS_VISIBLE,
            },
            headers={
                "Authorization": f"Bearer {response_admin_login_json.get('access_token')}"
            },
        )

        assert response_train_ai.status_code == 201
        response_train_ai_json: dict = response_train_ai.json()
        assert response_train_ai_json.get("task_id")

        task_result = AsyncResult(response_train_ai_json.get("task_id"))

        while task_result.state == "PENDING":
            time.sleep(0.5)

        ai = (
            data_base.query(AI)
            .filter_by(celery_task_id=response_train_ai_json.get("task_id"))
            .first()
        )

        assert ai.is_available == True
        assert ai.name == TEST_AI_NAME
        assert ai.is_visible == TEST_AI_IS_VISIBLE
        assert ai.description == TEST_AI_DESCRIPTION
        assert ai.finish_date != None
        assert ai.update_date != None
        assert ai.create_date != None
        assert ai.celery_task_id == response_train_ai_json.get("task_id")

        data_base.close()

    def test_get_ai(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        ai = data_base.query(AI).first()

        response_test = client.get(
            "/api/v1/ai/get_ai",
            params={
                "ai_id": ai.id,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 200
        response_test_json: dict = response_test.json()

        assert response_test_json.get("is_available") == True
        assert response_test_json.get("name") == TEST_AI_NAME
        assert response_test_json.get("is_visible") == TEST_AI_IS_VISIBLE
        assert response_test_json.get("description") == TEST_AI_DESCRIPTION
        assert response_test_json.get("create_date") != None

        if response_test_json.get("is_available"):
            assert response_test_json.get("finish_date") != None
            assert response_test_json.get("update_date") != None
        else:
            assert response_test_json.get("finish_date") == None
            assert response_test_json.get("update_date") == None

        assert response_test_json.get("celery_task_id") != None
        data_base.close()

    def test_get_ais(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        response_test = client.get(
            "/api/v1/ai/get_ais",
            params={
                # "is_available" : True,
                # "is_visible" : True,
                # "skip" : 0,
                # "limit" : 10,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 200
        response_test_json: dict = response_test.json()

        assert response_test_json.get("total") >= 0

        for ai in response_test_json.get("ais"):
            ai: dict

            assert ai.get("is_available") == True
            assert ai.get("name") == TEST_AI_NAME
            assert ai.get("is_visible") == TEST_AI_IS_VISIBLE
            assert ai.get("description") == TEST_AI_DESCRIPTION
            assert ai.get("create_date") != None

            if ai.get("is_available"):
                assert ai.get("finish_date") != None
                assert ai.get("update_date") != None

            assert ai.get("celery_task_id") != None
        data_base.close()

    def test_update_ai(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        ai = data_base.query(AI).first()

        response_test = client.put(
            "/api/v1/ai/update_ai",
            json={
                "ai_id": ai.id,
                "description": TEST_AI_DESCRIPTION_UPDATE,
                "is_visible": TEST_AI_IS_VISIBLE_UPDATE,
                "is_available": TEST_AI_IS_AVAILABLE_UPDATE,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        data_base.commit()

        assert response_test.status_code == 204

        assert ai.is_available == TEST_AI_IS_AVAILABLE_UPDATE
        assert ai.name == TEST_AI_NAME
        assert ai.is_visible == TEST_AI_IS_VISIBLE_UPDATE
        assert ai.description == TEST_AI_DESCRIPTION_UPDATE
        assert ai.create_date != None

        if ai.is_available:
            assert ai.finish_date != None
            assert ai.update_date != None

        assert ai.celery_task_id != None
        data_base.close()

    def test_delete_ai(self):
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        ai = data_base.query(AI).first()

        response_test = client.delete(
            "/api/v1/ai/delete_ai",
            params={
                "ai_id": ai.id,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        data_base.commit()

        assert response_test.status_code == 204

        ai = data_base.query(AI).first()

        assert ai == None

        data_base.close()


class TestAIlog:
    def test_data_base_init(self):
        data_base = session_local()
        data_base.query(AI).delete()
        data_base.query(AIlog).delete()
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

    def test_train_ai(self, celery_app, celery_worker):
        celery_worker.reload()
        data_base = session_local()

        response_admin_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_admin_login.status_code == 200
        response_admin_login_json: dict = response_admin_login.json()
        assert response_admin_login_json.get("access_token")
        assert response_admin_login_json.get("token_type")

        response_train_ai = client.post(
            "/api/v1/ai/train_ai",
            json={
                "name": TEST_AI_NAME,
                "description": TEST_AI_DESCRIPTION,
                "is_visible": TEST_AI_IS_VISIBLE,
            },
            headers={
                "Authorization": f"Bearer {response_admin_login_json.get('access_token')}"
            },
        )

        assert response_train_ai.status_code == 201
        response_train_ai_json: dict = response_train_ai.json()
        assert response_train_ai_json.get("task_id")

        task_result = AsyncResult(response_train_ai_json.get("task_id"))

        while task_result.state == "PENDING":
            time.sleep(0.5)

        ai = (
            data_base.query(AI)
            .filter_by(celery_task_id=response_train_ai_json.get("task_id"))
            .first()
        )

        assert ai.is_available == True
        assert ai.name == TEST_AI_NAME
        assert ai.is_visible == TEST_AI_IS_VISIBLE
        assert ai.description == TEST_AI_DESCRIPTION
        assert ai.finish_date != None
        assert ai.update_date != None
        assert ai.create_date != None
        assert ai.celery_task_id == response_train_ai_json.get("task_id")

        data_base.close()

    def test_ai_infer(self, celery_app, celery_worker):
        celery_worker.reload()
        data_base = session_local()

        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        ai = data_base.query(AI).first()
        response_test = client.post(
            "/api/v1/ai/ai_infer",
            json={
                "ai_id": ai.id,
                "description": TEST_AI_LOG_DESCRIPTION,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 201
        response_test_json: dict = response_test.json()
        assert response_test_json.get("task_id")

        task_result = AsyncResult(response_test_json.get("task_id"))

        while task_result.state == "PENDING":
            time.sleep(0.5)

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=response_login_json.get("access_token")
        ).get("user_id")

        ailog = (
            data_base.query(AIlog)
            .filter_by(celery_task_id=response_test_json.get("task_id"))
            .first()
        )

        assert ailog.user_id == user_id
        assert ailog.ai_id == ai.id
        assert ailog.description == TEST_AI_LOG_DESCRIPTION
        assert ailog.finish_date != None
        assert ailog.update_date != None
        assert ailog.create_date != None
        assert ailog.result != None
        assert ailog.is_finished != None
        assert ailog.celery_task_id == response_test_json.get("task_id")
        data_base.close()

    def test_get_ailog(self):
        data_base = session_local()
        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        ailog = data_base.query(AIlog).first()

        response_test = client.get(
            "/api/v1/ai/get_ailog",
            params={
                "ailog_id": ailog.id,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 200
        response_test_json: dict = response_test.json()

        user_id = validate_and_decode_user_access_token(data_base=data_base, token=
            response_login_json.get("access_token")
        ).get("user_id")

        assert response_test_json.get("user_id") == user_id
        assert response_test_json.get("ai_id") > 0
        assert response_test_json.get("description") == TEST_AI_LOG_DESCRIPTION
        assert response_test_json.get("create_date") != None
        assert response_test_json.get("result") != None
        assert response_test_json.get("is_finished") != None

        if response_test_json.get("is_available"):
            assert response_test_json.get("finish_date") != None
            assert response_test_json.get("update_date") != None

        assert response_test_json.get("celery_task_id") == ailog.celery_task_id
        data_base.close()

    def test_get_ailogs(self):
        data_base = session_local()
        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        ai = data_base.query(AIlog).first()

        user_id = validate_and_decode_user_access_token(data_base=data_base, token=
            response_login_json.get("access_token")
        ).get("user_id")

        response_test = client.get(
            "/api/v1/ai/get_ailogs",
            params={
                # "user_id" : user_id,
                # "ai_id" : ai.id,
                # "skip" : 0,
                # "limit" : 10,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        assert response_test.status_code == 200
        response_test_json: dict = response_test.json()

        assert response_test_json.get("total") >= 0

        for ailog in response_test_json.get("ailogs"):
            ailog: dict

            assert ailog.get("user_id") > 0
            assert ailog.get("ai_id") > 0
            assert ailog.get("description") == TEST_AI_LOG_DESCRIPTION
            assert ailog.get("create_date") != None
            assert ailog.get("result") != None
            assert ailog.get("is_finished") != None

            if ailog.get("is_available"):
                assert ailog.get("finish_date") != None
                assert ailog.get("update_date") != None

            assert ailog.get("celery_task_id") != None
        data_base.close()

    def test_update_ailog(self):
        data_base = session_local()
        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        ailog = data_base.query(AIlog).first()

        response_test = client.put(
            "/api/v1/ai/update_ailog",
            json={
                "ailog_id": ailog.id,
                "description": TEST_AI_LOG_DESCRIPTION_UPDATE,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        data_base.commit()

        assert response_test.status_code == 204

        user_id = validate_and_decode_user_access_token(data_base=data_base, token=
            response_login_json.get("access_token")
        ).get("user_id")

        assert ailog.user_id > 0
        assert ailog.ai_id > 0
        assert ailog.description == TEST_AI_LOG_DESCRIPTION_UPDATE
        assert ailog.create_date != None
        assert ailog.result != None
        assert ailog.is_finished != None

        if ailog.is_finished:
            assert ailog.finish_date != None
            assert ailog.update_date != None

        assert ailog.celery_task_id != None
        data_base.close()

    def test_delete_ailog(self):
        data_base = session_local()
        response_login = client.post(
            "/api/v1/user/login_user",
            data={"username": TEST_ADMIN_ID, "password": TEST_ADMIN_PASSWORD1},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        assert response_login.status_code == 200
        response_login_json: dict = response_login.json()
        assert response_login_json.get("access_token")
        assert response_login_json.get("token_type")

        ailog = data_base.query(AIlog).first()

        response_test = client.delete(
            "/api/v1/ai/delete_ailog",
            params={
                "ailog_id": ailog.id,
            },
            headers={
                "Authorization": f"Bearer {response_login_json.get('access_token')}"
            },
        )

        data_base.commit()

        assert response_test.status_code == 204

        ailog = data_base.query(AIlog).first()

        assert ailog == None
        data_base.close()

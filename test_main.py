from pytest import MonkeyPatch

from fastapi.testclient import TestClient

from sqlalchemy import delete, text

from main import app
import models
from database import session_local


client = TestClient(app)


class MainTestMethods:
    def data_base_init(self):
        data_base = session_local()
        data_base.execute(delete(models.JWTAccessTokenBlackList))
        data_base.execute(delete(models.JWTRefreshTokenList))
        data_base.execute(delete(models.PostFile))
        data_base.execute(delete(models.CommentFile))
        data_base.execute(delete(models.UserChatSessionTable))
        data_base.execute(delete(models.UserPermissionTable))
        data_base.execute(delete(models.AIlog))
        data_base.execute(delete(models.AI))
        data_base.execute(delete(models.Chat))
        data_base.execute(delete(models.ChatSession))
        data_base.execute(delete(models.Comment))
        data_base.execute(delete(models.Post))
        data_base.execute(delete(models.Board))
        data_base.execute(delete(models.User))

        for value in data_base.execute(text("SELECT * FROM sqlite_sequence")).all():
            data_base.execute(
                text(f'UPDATE sqlite_sequence SET seq = 0 WHERE name = "{value[0]}"')
            )

        data_base.commit()
        data_base.close()

    def patch(self):
        def patch_task():
            a = input()
            b = input()
            return (a, b)

        fake_input = iter(["13", "39", "44", "df"]).__next__
        monkeypatch = MonkeyPatch()
        monkeypatch.setattr("builtins.input", fake_input)

        assert patch_task() == ("13", "39")
        assert patch_task() == ("44", "df")

    def add_task(self, celery_app, celery_worker):
        @celery_app.task
        def mul(x, y):
            return x * y

        celery_worker.reload()
        assert mul.delay(2, 2).get() == 4

    def read_main(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello, FastAPI!"}


main_test_methods = MainTestMethods()


class TestMain:
    def test_patch(self):
        main_test_methods.patch()

    def test_add_task(self, celery_app, celery_worker):
        main_test_methods.add_task(celery_app=celery_app, celery_worker=celery_worker)

    def test_data_base_init(self):
        main_test_methods.data_base_init()

    def test_read_main(self):
        main_test_methods.read_main()

from pytest import MonkeyPatch

from fastapi.testclient import TestClient

from main import app
from models import User
from database import session_local


client = TestClient(app)


class TestMain:
    def test_patch(self):
        def patch_task():
            a = input()
            b = input()
            return (a, b)

        fake_input = iter(["13", "39", "44", "df"]).__next__
        monkeypatch = MonkeyPatch()
        monkeypatch.setattr("builtins.input", fake_input)

        assert patch_task() == ("13", "39")
        assert patch_task() == ("44", "df")
        
    def test_add_task(self, celery_app, celery_worker):
        @celery_app.task
        def mul(x, y):
            return x * y

        celery_worker.reload()
        assert mul.delay(2, 2).get() == 4

    def test_data_base_init(self):
        data_base = session_local()
        data_base.query(User).delete()
        data_base.commit()
        data_base.close()

    def test_read_main(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello, FastAPI!"}

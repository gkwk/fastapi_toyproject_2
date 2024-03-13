import os
import pytest

celery_app_broker_url = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672")
@pytest.fixture(scope="session")
def celery_config():
    return {
        "broker_url": celery_app_broker_url,
        "result_backend": "db+sqlite:///celery.sqlite",
    }
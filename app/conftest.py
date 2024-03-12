import pytest


@pytest.fixture(scope="session")
def celery_config():
    return {
        "broker_url": "amqp://",
        "result_backend": "db+sqlite:///celery.sqlite",
    }
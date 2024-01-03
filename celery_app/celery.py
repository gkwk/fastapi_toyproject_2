import os
import time,datetime

from celery import Celery

app = Celery(__name__)
app.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672")
app.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "db+sqlite:///celery.sqlite")

app.autodiscover_tasks()


@app.task(name="test_task")
def create_task():
    timer = datetime.datetime.now()
    time.sleep(5)
    timerend = datetime.datetime.now()
    return (timerend-timer).seconds
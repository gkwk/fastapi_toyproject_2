import os
import time, datetime

from celery import Celery
from celery.schedules import crontab


import domain.ai
import domain.board
import models

celery_app_broker_url = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672")

celery_app = Celery(__name__, backend="db+sqlite:///db/celery.sqlite", broker=celery_app_broker_url,)
# celery_app.conf.broker_url = os.environ.get(
#     "CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672"
# )
# celery_app.conf.result_backend = os.environ.get(
#     "CELERY_RESULT_BACKEND", "db+sqlite:///celery.sqlite"
# )

celery_app.autodiscover_tasks(["domain.ai","domain.board"])



celery_app.conf.beat_schedule = {
    "update-post-view-counts-every-minute": {
        "task": "update_post_view_counts",
        "schedule": 10.0,
        "args" : (None,)
    },
}
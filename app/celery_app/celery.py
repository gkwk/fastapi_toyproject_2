import os
import time, datetime

from celery import Celery

import domain.ai
import models

celery_app_broker_url = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672")

celery_app = Celery(__name__, backend="db+sqlite:///celery.sqlite", broker=celery_app_broker_url,)
# celery_app.conf.broker_url = os.environ.get(
#     "CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672"
# )
# celery_app.conf.result_backend = os.environ.get(
#     "CELERY_RESULT_BACKEND", "db+sqlite:///celery.sqlite"
# )

celery_app.autodiscover_tasks(["domain.ai"])

import os
from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery(
    "smartmatching_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.imports = ["app.tasks.sync"]

celery_app.conf.timezone = "Europe/Kyiv"

celery_app.conf.beat_schedule = {
    "daily-startup-sync": {
        "task": "app.tasks.sync.sync_startups_task",
        "schedule": crontab(hour=8, minute=0),
    },
}
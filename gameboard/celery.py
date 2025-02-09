from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

from django.conf import settings

from datetime import timedelta

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gameboard.settings")

app = Celery("gameboard")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# @app.task(bind=True)
# def debug_task(self):
#     print(f"Request: {self.request!r}")


app.conf.task_create_missing_queues = True

app.conf.beat_schedule = {
    # "debug_task": {
    #     "task": "gameboard.celery.debug_task",
    #     "schedule": 10,
    # },
    "cache_popularity_factors_and_max_values": {
        "task": "gameboard.games.tasks.cache_popularity_factors_and_max_values",
        "schedule": crontab(hour=0, minute=0),  # Run at 12 AM every day
    },
    "refresh_game_popularity": {
        "task": "gameboard.games.tasks.refresh_game_popularity",
        # "schedule": timedelta(minutes=5),  # Run every 5 minutes
        # "schedule": crontab(minute="*/1"),  # Run every 1 minutes
        "schedule": 60,  # Run every 1 minutes
    },
}

app.autodiscover_tasks()

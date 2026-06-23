# app/tasks/celery_app.py
"""
Celery Application
Land Intelligence System

Creates and configures the Celery app instance used by both
background_workers (task definitions) and scheduled_tasks (beat schedule).

Broker  : Redis (configured via REDIS_URL env var, default localhost)
Backend : Redis (same instance, separate DB index)
"""

import logging
from celery import Celery
from celery.schedules import crontab

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Broker / backend URLs
# ---------------------------------------------------------------------------
# We read directly from the environment here rather than importing settings
# so that this module remains importable even before pydantic-settings loads.

import os

REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

# ---------------------------------------------------------------------------
# Celery app
# ---------------------------------------------------------------------------

celery_app = Celery(
    "land_intelligence",
    broker=REDIS_URL,
    backend=RESULT_BACKEND,
    include=["app.tasks.background_workers"],
)

celery_app.conf.update(
    # Serialisation
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # Timezone
    timezone="Africa/Kigali",
    enable_utc=True,
    # Task behaviour
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    # Result expiry (24 hours)
    result_expires=86400,
    # Worker concurrency — keep low; DB ops are I/O bound but we bridge via asyncio.run()
    worker_concurrency=4,
    worker_prefetch_multiplier=1,
)

# ---------------------------------------------------------------------------
# Celery Beat periodic schedule
# ---------------------------------------------------------------------------

celery_app.conf.beat_schedule = {
    # Full local backup every day at 02:00 Kigali time
    "daily-local-backup": {
        "task": "app.tasks.background_workers.trigger_full_local_backup",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "backup"},
    },
    # Retry failed backup jobs every 30 minutes
    "retry-failed-backup-jobs": {
        "task": "app.tasks.background_workers.retry_failed_backup_jobs",
        "schedule": crontab(minute="*/30"),
        "options": {"queue": "maintenance"},
    },
    # Integrity check on the most recent local backup every day at 03:00
    "daily-integrity-check": {
        "task": "app.tasks.background_workers.check_latest_backup_integrity",
        "schedule": crontab(hour=3, minute=0),
        "options": {"queue": "backup"},
    },
}

celery_app.conf.task_queues = {
    "backup": {},
    "maintenance": {},
    "default": {},
}
celery_app.conf.task_default_queue = "default"# app/tasks/celery_app.py

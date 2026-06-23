# app/tasks/scheduled_tasks.py
# app/tasks/scheduled_tasks.py
"""
Scheduled Tasks
Land Intelligence System

Two scheduling modes are supported:

1. Celery Beat (production)
   The beat_schedule is defined in celery_app.py and runs automatically
   when you start the beat worker:
       celery -A app.tasks.celery_app beat --loglevel=info

2. Lightweight scheduler using the `schedule` library (development / single-process)
   Call run_scheduler() from a management script or a startup thread when
   Redis / Celery are not available.

   Example (add to main.py startup event for dev):
       import threading
       from app.tasks.scheduled_tasks import run_scheduler
       threading.Thread(target=run_scheduler, daemon=True).start()
"""

import asyncio
import logging
import time
import threading

import schedule

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Async job implementations (reused by both scheduling modes)
# ---------------------------------------------------------------------------

async def _daily_local_backup_job() -> None:
    """Run a full local backup and log the outcome."""
    from app.tasks.background_workers import _run_full_local_backup
    try:
        result = await _run_full_local_backup()
        logger.info("Scheduled daily backup completed: %s", result)
    except Exception as exc:
        logger.error("Scheduled daily backup failed: %s", exc, exc_info=True)


async def _integrity_check_job() -> None:
    """Run an integrity check on the latest local backup."""
    from app.tasks.background_workers import _check_latest_integrity
    try:
        result = await _check_latest_integrity()
        logger.info("Scheduled integrity check result: %s", result)
    except Exception as exc:
        logger.error("Scheduled integrity check failed: %s", exc, exc_info=True)


async def _retry_failed_jobs_job() -> None:
    """Re-queue failed backup jobs."""
    from app.tasks.background_workers import _retry_failed_jobs
    try:
        result = await _retry_failed_jobs()
        logger.info("Scheduled retry pass result: %s", result)
    except Exception as exc:
        logger.error("Scheduled retry pass failed: %s", exc, exc_info=True)


# ---------------------------------------------------------------------------
# Synchronous wrappers (required by the `schedule` library)
# ---------------------------------------------------------------------------

def _run_async(coro) -> None:
    """Run an async coroutine from a synchronous schedule callback."""
    asyncio.run(coro())


# ---------------------------------------------------------------------------
# Schedule registration
# ---------------------------------------------------------------------------

def register_schedules() -> None:
    """
    Register all periodic jobs with the `schedule` library.
    Call once before starting the scheduler loop.
    """
    # Full local backup every day at 02:00
    schedule.every().day.at("02:00").do(_run_async, _daily_local_backup_job)

    # Integrity check every day at 03:00
    schedule.every().day.at("03:00").do(_run_async, _integrity_check_job)

    # Retry failed jobs every 30 minutes
    schedule.every(30).minutes.do(_run_async, _retry_failed_jobs_job)

    logger.info(
        "Scheduled tasks registered: daily backup at 02:00, "
        "integrity check at 03:00, retry every 30 min."
    )


def run_scheduler(stop_event: threading.Event | None = None) -> None:
    """
    Blocking scheduler loop. Intended to run in a daemon thread.

    Args:
        stop_event: optional threading.Event; when set, the loop exits cleanly.

    Usage::

        import threading
        from app.tasks.scheduled_tasks import run_scheduler

        stop = threading.Event()
        t = threading.Thread(target=run_scheduler, args=(stop,), daemon=True)
        t.start()

        # To stop:
        stop.set()
    """
    register_schedules()
    logger.info("Lightweight scheduler started.")

    while not (stop_event and stop_event.is_set()):
        schedule.run_pending()
        time.sleep(60)  # check every minute

    logger.info("Lightweight scheduler stopped.")


# ---------------------------------------------------------------------------
# Celery Beat helper — dispatch tasks to worker queue
# ---------------------------------------------------------------------------

def dispatch_daily_backup() -> str:
    """
    Manually enqueue a full local backup via Celery.
    Returns the Celery task ID.

    Usage::

        from app.tasks.scheduled_tasks import dispatch_daily_backup
        task_id = dispatch_daily_backup()
    """
    from app.tasks.background_workers import trigger_full_local_backup
    result = trigger_full_local_backup.apply_async(queue="backup")
    logger.info("Dispatched daily backup task: %s", result.id)
    return result.id


def dispatch_integrity_check() -> str:
    """Manually enqueue an integrity check via Celery."""
    from app.tasks.background_workers import check_latest_backup_integrity
    result = check_latest_backup_integrity.apply_async(queue="backup")
    logger.info("Dispatched integrity check task: %s", result.id)
    return result.id


def dispatch_retry_failed() -> str:
    """Manually enqueue a retry pass via Celery."""
    from app.tasks.background_workers import retry_failed_backup_jobs
    result = retry_failed_backup_jobs.apply_async(queue="maintenance")
    logger.info("Dispatched retry task: %s", result.id)
    return result.id
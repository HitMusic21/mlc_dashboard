"""
Celery application configuration for async task processing.
"""
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# Initialize Celery app with Redis broker and backend
celery_app = Celery(
    settings.PROJECT_NAME,
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Configure Celery
celery_app.conf.update(
    # Task routing
    task_routes={
        "app.tasks.catalog_processing.*": {"queue": "catalog"},
        "app.tasks.cleanup.*": {"queue": "cleanup"},
    },
    # Worker settings
    worker_prefetch_multiplier=1,  # Process one task at a time per worker
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks to prevent memory leaks
    # Task execution settings
    task_acks_late=True,  # Acknowledge task after execution (for retries)
    task_reject_on_worker_lost=True,  # Reject task if worker crashes
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
    },
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Retry settings
    task_default_retry_delay=60,  # Retry after 60 seconds
    task_max_retries=3,
)

# Optional: Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Clean up old uploads every day at 2 AM
    "cleanup-old-uploads": {
        "task": "app.tasks.cleanup.cleanup_old_uploads",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "cleanup"},
    },
    # Clean up expired cache entries every hour
    "cleanup-cache": {
        "task": "app.tasks.cleanup.cleanup_cache",
        "schedule": crontab(minute=0),
        "options": {"queue": "cleanup"},
    },
}

# Auto-discover tasks from app.tasks module
celery_app.autodiscover_tasks(["app.tasks"])


# Task base class for custom error handling
class BaseTask(celery_app.Task):
    """Base task with custom error handling."""

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True  # Exponential backoff
    retry_backoff_max = 600  # Max 10 minutes
    retry_jitter = True  # Add random jitter to backoff

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails after all retries."""
        print(f"Task {task_id} failed: {exc}")
        # You can add custom logging or notifications here
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried."""
        print(f"Task {task_id} retry: {exc}")
        super().on_retry(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds."""
        print(f"Task {task_id} succeeded")
        super().on_success(retval, task_id, args, kwargs)


# Set default base class
celery_app.Task = BaseTask


if __name__ == "__main__":
    # Start worker with: celery -A celery_app worker --loglevel=info -Q catalog
    # Start beat with: celery -A celery_app beat --loglevel=info
    celery_app.start()

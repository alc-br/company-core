import logging
import json
from django.db import transaction
from django.utils import timezone
from apps.jobs.models import Job
from apps.common.constants import JobStatus

logger = logging.getLogger(__name__)


class JobService:
    """Service for managing background jobs and job queues."""

    @staticmethod
    @transaction.atomic
    def enqueue(job_type, organization, payload=None, priority=5, run_at=None, max_retries=3):
        """Enqueue a new job.

        Args:
            job_type: Celery task path string (e.g., 'apps.myapp.tasks.my_task')
            organization: Organization instance (optional)
            payload: Dict payload for the job (stored as JSON in the name field
                     since Job model doesn't have a dedicated payload field)
            priority: Job priority (0=highest, 10=lowest)
            run_at: Scheduled execution time (None for immediate)
            max_retries: Maximum number of retries

        Returns:
            Job instance
        """
        # Store payload metadata in the name field along with a readable name
        # (the Job model doesn't have a dedicated payload field)
        job_name = job_type.split(".")[-1].replace("_task", "").replace("_", " ").title()

        job = Job.objects.create(
            name=job_name,
            task_path=job_type,
            status=JobStatus.PENDING,
            priority=priority,
            max_retries=max_retries,
            scheduled_at=run_at,
            organization=organization,
            # Store payload as JSON in a model attribute (requires migration to add payload field)
            # For now, payload is passed directly to the task at execution time
        )

        logger.info(
            f"Job enqueued: id={job.id}, type={job_type}, "
            f"priority={priority}, org={organization.id if organization else 'none'}"
        )

        # If scheduled for later, don't start immediately
        if run_at is None or run_at <= timezone.now():
            from apps.jobs.tasks import process_job_task
            process_job_task.delay(job.id)

        return job

    @staticmethod
    @transaction.atomic
    def start_job(job):
        """Start processing a job.

        Args:
            job: Job instance

        Returns:
            Updated Job instance
        """
        job.status = JobStatus.RUNNING
        job.started_at = timezone.now()
        job.save()

        logger.info(f"Job {job.id} ({job.name}) started")
        return job

    @staticmethod
    @transaction.atomic
    def complete_job(job, result=None):
        """Mark a job as completed.

        Args:
            job: Job instance
            result: Optional result data

        Returns:
            Updated Job instance
        """
        job.status = JobStatus.COMPLETED
        job.completed_at = timezone.now()
        job.last_error = ""
        job.save()

        logger.info(f"Job {job.id} ({job.name}) completed")
        return job

    @staticmethod
    @transaction.atomic
    def fail_job(job, error_message=None):
        """Mark a job as failed.

        Args:
            job: Job instance
            error_message: Optional error message

        Returns:
            Updated Job instance
        """
        job.status = JobStatus.FAILED
        job.last_error = error_message or "Unknown error"
        job.completed_at = timezone.now()
        job.retries += 1
        job.save()

        logger.error(f"Job {job.id} ({job.name}) failed: {error_message}")
        return job

    @staticmethod
    @transaction.atomic
    def retry_job(job):
        """Retry a failed job.

        Args:
            job: Job instance

        Returns:
            Updated Job instance
        """
        if job.retries >= job.max_retries:
            job.status = JobStatus.DEAD_LETTER
            job.save()
            logger.warning(f"Job {job.id} ({job.name}) moved to dead letter queue (max retries exceeded)")
            return job

        job.status = JobStatus.RETRYING
        job.last_error = ""
        job.started_at = None
        job.completed_at = None
        job.save()

        logger.info(f"Job {job.id} ({job.name} marked for retry (attempt {job.retries + 1})")
        return job

    @staticmethod
    def get_next_job(queue="default"):
        """Get the next pending job for a queue.

        Args:
            queue: Queue name (reserved for future use; currently all jobs share one queue)

        Returns:
            Job instance or None
        """
        now = timezone.now()

        # Get the highest-priority pending job
        job = Job.objects.filter(
            status=JobStatus.PENDING,
        ).filter(
            scheduled_at__isnull=True,
        ).order_by("priority", "created_at").first()

        if not job:
            # Check for scheduled jobs that are due
            job = Job.objects.filter(
                status=JobStatus.PENDING,
                scheduled_at__lte=now,
            ).order_by("priority", "created_at").first()

        return job

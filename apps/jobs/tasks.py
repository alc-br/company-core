import logging
import importlib
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_job_task(self, job_id):
    """Process a job from the queue."""
    from apps.jobs.models import Job
    from apps.jobs.services import JobService
    from apps.common.constants import JobStatus

    try:
        job = Job.objects.get(id=job_id)

        if job.status == JobStatus.COMPLETED:
            logger.info(f"Job {job_id} already completed")
            return None

        if job.status == JobStatus.DEAD_LETTER:
            logger.info(f"Job {job_id} is in dead letter queue")
            return None

        # Start the job
        job = JobService.start_job(job)

        try:
            # Dynamically import and execute the task
            task_path = job.task_path
            module_path, func_name = task_path.rsplit(".", 1) if "." in task_path else (task_path, None)

            if not func_name:
                raise ValueError(f"Invalid task path: {task_path}")

            module = importlib.import_module(module_path)
            task_func = getattr(module, func_name, None)

            if not task_func or not callable(task_func):
                raise ValueError(f"Task function not found: {task_path}")

            # Execute the task function
            result = task_func(job)
            JobService.complete_job(job, result=result)

            logger.info(f"Job {job_id} ({job.name}) completed successfully")
            return {"job_id": job_id, "status": "completed"}
        except Exception as task_exc:
            JobService.fail_job(job, error_message=str(task_exc))
            logger.error(f"Job {job_id} ({job.name}) failed: {task_exc}")
            return {"job_id": job_id, "status": "failed", "error": str(task_exc)}

    except Job.DoesNotExist:
        logger.error(f"Job {job_id} not found")
        return None
    except Exception as exc:
        logger.error(f"Failed to process job {job_id}: {exc}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def retry_failed_jobs_task(self):
    """Retry all failed jobs that haven't exceeded max retries."""
    from apps.jobs.models import Job
    from apps.jobs.services import JobService
    from apps.common.constants import JobStatus

    try:
        failed_jobs = Job.objects.filter(
            status=JobStatus.FAILED,
        )

        retried_count = 0
        dead_letter_count = 0

        for job in failed_jobs:
            if job.retries >= job.max_retries:
                job.status = JobStatus.DEAD_LETTER
                job.save()
                dead_letter_count += 1
                logger.info(f"Job {job.id} moved to dead letter queue (max retries exceeded)")
            else:
                JobService.retry_job(job)
                process_job_task.delay(job.id)
                retried_count += 1
                logger.info(f"Job {job.id} queued for retry (attempt {job.retries + 1})")

        logger.info(
            f"Retry failed jobs complete: {retried_count} retried, "
            f"{dead_letter_count} moved to dead letter"
        )
        return {"retried": retried_count, "dead_letter": dead_letter_count}
    except Exception as exc:
        logger.error(f"Failed to retry failed jobs: {exc}")
        self.retry(exc=exc)

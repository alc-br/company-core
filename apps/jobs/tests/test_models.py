import pytest
from apps.jobs.models import Job


class TestJob:
    def test_job_creation(self):
        job = Job(name="daily_report", task_path="apps.billing.tasks.generate_invoice")
        assert job.name == "daily_report"
        assert job.priority == 5
        assert job.max_retries == 3

    def test_job_str(self):
        job = Job(name="sync_data", task_path="apps.sync.tasks.run")
        assert "sync_data" in str(job)

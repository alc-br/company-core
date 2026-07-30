import logging
import time
from celery import shared_task
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def execute_workflow_task(self, workflow_execution_id):
    """Execute a workflow step by step."""
    from apps.workflows.models import WorkflowExecution, WorkflowStepLog
    from apps.workflows.services import WorkflowService
    from apps.common.constants import WorkflowExecutionStatus

    try:
        execution = WorkflowExecution.objects.select_related("workflow").get(id=workflow_execution_id)

        if execution.status == WorkflowExecutionStatus.COMPLETED:
            logger.info(f"Workflow execution {workflow_execution_id} already completed")
            return None

        if execution.status == WorkflowExecutionStatus.FAILED:
            logger.info(f"Workflow execution {workflow_execution_id} is failed, use retry instead")
            return None

        # Mark as running
        execution.status = WorkflowExecutionStatus.RUNNING
        execution.started_at = timezone.now()
        execution.save()

        steps_config = execution.workflow.steps_config
        if not steps_config or not isinstance(steps_config, list):
            logger.error(f"Workflow {execution.workflow.id} has no steps configured")
            execution.status = WorkflowExecutionStatus.FAILED
            execution.save()
            return None

        # Execute each step sequentially
        output_data = dict(execution.input_data)
        for step_index, step_config in enumerate(steps_config):
            if execution.current_step > step_index:
                continue  # Skip already completed steps

            step = {
                "index": step_index,
                "name": step_config.get("name", f"step_{step_index}"),
                "type": step_config.get("type", "action"),
                "config": step_config.get("config", {}),
            }

            try:
                result = WorkflowService.execute_step(execution, step)
                output_data.update(result if isinstance(result, dict) else {"output": result})

                WorkflowService.complete_step(execution, step, result)
                execution.current_step = step_index + 1
                execution.output_data = output_data
                execution.save()
            except Exception as step_exc:
                WorkflowService.fail_step(execution, step, str(step_exc))
                execution.output_data = output_data
                execution.save()
                logger.error(
                    f"Workflow execution {workflow_execution_id} failed at step "
                    f"{step['name']}: {step_exc}"
                )
                return {
                    "execution_id": workflow_execution_id,
                    "status": "failed",
                    "failed_step": step["name"],
                    "error": str(step_exc),
                }

        # All steps completed
        execution.status = WorkflowExecutionStatus.COMPLETED
        execution.completed_at = timezone.now()
        execution.output_data = output_data
        execution.save()

        logger.info(f"Workflow execution {workflow_execution_id} completed successfully")
        return {
            "execution_id": workflow_execution_id,
            "status": "completed",
            "steps_executed": len(steps_config),
        }
    except WorkflowExecution.DoesNotExist:
        logger.error(f"Workflow execution {workflow_execution_id} not found")
        return None
    except Exception as exc:
        logger.error(f"Failed to execute workflow {workflow_execution_id}: {exc}")
        try:
            execution = WorkflowExecution.objects.get(id=workflow_execution_id)
            execution.status = WorkflowExecutionStatus.FAILED
            execution.save()
        except Exception:
            pass
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def retry_workflow_task(self, workflow_execution_id):
    """Retry a failed workflow execution."""
    from apps.workflows.models import WorkflowExecution
    from apps.common.constants import WorkflowExecutionStatus

    try:
        execution = WorkflowExecution.objects.get(id=workflow_execution_id)

        if execution.status != WorkflowExecutionStatus.FAILED:
            logger.warning(
                f"Workflow execution {workflow_execution_id} is not failed "
                f"(status={execution.status}), skipping retry"
            )
            return None

        # Reset to pending and re-execute
        execution.status = WorkflowExecutionStatus.PENDING
        execution.started_at = None
        execution.completed_at = None
        execution.last_error = ""
        execution.save()

        # Clear step logs and re-execute
        execution.step_logs.all().delete()

        logger.info(f"Workflow execution {workflow_execution_id} queued for retry")
        execute_workflow_task.delay(workflow_execution_id)

        return {"execution_id": workflow_execution_id, "status": "retrying"}
    except WorkflowExecution.DoesNotExist:
        logger.error(f"Workflow execution {workflow_execution_id} not found for retry")
        return None
    except Exception as exc:
        logger.error(f"Failed to retry workflow {workflow_execution_id}: {exc}")
        self.retry(exc=exc)

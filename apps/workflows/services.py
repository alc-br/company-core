import logging
import time
import importlib
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from apps.workflows.models import Workflow, WorkflowExecution, WorkflowStepLog
from apps.common.constants import WorkflowExecutionStatus

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service for managing workflow definitions and executions."""

    @staticmethod
    @transaction.atomic
    def start_workflow(workflow, organization, user, input_data=None):
        """Start a new workflow execution.

        Args:
            workflow: Workflow model instance
            organization: Organization model instance
            user: User initiating the workflow
            input_data: Optional dict of input data

        Returns:
            WorkflowExecution instance
        """
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            organization=organization,
            status=WorkflowExecutionStatus.PENDING,
            current_step=0,
            input_data=input_data or {},
            output_data={},
        )

        logger.info(
            f"Workflow '{workflow.name}' started: execution_id={execution.id}, "
            f"initiated by user={user.id}"
        )

        # Trigger async execution
        from apps.workflows.tasks import execute_workflow_task
        execute_workflow_task.delay(execution.id)

        return execution

    @staticmethod
    @transaction.atomic
    def execute_step(execution, step):
        """Execute a single workflow step.

        Args:
            execution: WorkflowExecution instance
            step: dict with keys: index, name, type, config

        Returns:
            Step execution result (dict or any)

        Raises:
            Exception on step failure
        """
        step_type = step.get("type", "action")
        step_config = step.get("config", {})
        step_name = step.get("name", f"step_{step.get('index', 0)}")

        logger.info(
            f"Executing step '{step_name}' (type={step_type}) "
            f"for execution {execution.id}"
        )

        if step_type == "action":
            result = WorkflowService._execute_action_step(step_config, execution)
        elif step_type == "condition":
            result = WorkflowService._execute_condition_step(step_config, execution)
        elif step_type == "delay":
            result = WorkflowService._execute_delay_step(step_config, execution)
        elif step_type == "parallel":
            result = WorkflowService._execute_parallel_step(step_config, execution)
        elif step_type == "http_call":
            result = WorkflowService._execute_http_call_step(step_config, execution)
        else:
            raise ValueError(f"Unknown step type: {step_type}")

        return result

    @staticmethod
    def _execute_action_step(config, execution):
        """Execute an action step — calls a configured handler."""
        handler_path = config.get("handler_path", "")
        if not handler_path:
            raise ValueError("Action step requires 'handler_path' in config")

        module_path, func_name = handler_path.rsplit(".", 1) if "." in handler_path else (handler_path, None)
        if not func_name:
            raise ValueError(f"Invalid handler path: {handler_path}")

        module = importlib.import_module(module_path)
        handler = getattr(module, func_name, None)

        if not handler or not callable(handler):
            raise ValueError(f"Handler not found: {handler_path}")

        kwargs = config.get("kwargs", {})
        # Merge execution input data with step-specific kwargs
        merged_kwargs = {**execution.input_data, **kwargs}
        return handler(execution=execution, **merged_kwargs)

    @staticmethod
    def _execute_condition_step(config, execution):
        """Execute a condition step — evaluates a condition and branches."""
        condition_field = config.get("condition_field", "")
        condition_value = config.get("condition_value")
        condition_operator = config.get("operator", "equals")

        # Get the value from execution output data
        actual_value = execution.output_data.get(condition_field)

        result = False
        if condition_operator == "equals":
            result = actual_value == condition_value
        elif condition_operator == "not_equals":
            result = actual_value != condition_value
        elif condition_operator == "contains":
            result = condition_value in str(actual_value) if actual_value else False
        elif condition_operator == "greater_than":
            result = actual_value > condition_value if actual_value is not None else False
        elif condition_operator == "less_than":
            result = actual_value < condition_value if actual_value is not None else False
        elif condition_operator == "exists":
            result = actual_value is not None
        elif condition_operator == "not_exists":
            result = actual_value is None

        logger.info(f"Condition step evaluated: {condition_field} {condition_operator} {condition_value} = {result}")
        return {"condition_result": result, "branch": "true" if result else "false"}

    @staticmethod
    def _execute_delay_step(config, execution):
        """Execute a delay/wait step."""
        delay_seconds = config.get("delay_seconds", 0)
        if delay_seconds > 0:
            import time
            time.sleep(delay_seconds)

        logger.info(f"Delay step completed: waited {delay_seconds}s")
        return {"delayed_seconds": delay_seconds}

    @staticmethod
    def _execute_parallel_step(config, execution):
        """Execute a parallel step — runs multiple actions concurrently."""
        steps = config.get("steps", [])
        if not steps:
            return {"parallel_results": []}

        # Execute in sequence within the Celery task (true parallelism
        # would require sub-tasks, but we keep it simple here)
        results = []
        for sub_step in steps:
            try:
                sub_result = WorkflowService._execute_action_step(sub_step, execution)
                results.append({"status": "success", "result": sub_result})
            except Exception as e:
                results.append({"status": "failed", "error": str(e)})
                logger.error(f"Parallel sub-step failed: {e}")

        success_count = sum(1 for r in results if r["status"] == "success")
        logger.info(f"Parallel step completed: {success_count}/{len(steps)} succeeded")
        return {"parallel_results": results}

    @staticmethod
    def _execute_http_call_step(config, execution):
        """Execute an HTTP call step."""
        import urllib.request
        import urllib.error
        import json

        url = config.get("url", "")
        method = config.get("method", "GET").upper()
        headers = config.get("headers", {})
        body = config.get("body", {})
        timeout = config.get("timeout", 30)

        if not url:
            raise ValueError("HTTP call step requires 'url' in config")

        # Template variables from execution data
        for key, value in execution.output_data.items():
            url = url.replace(f"{{{{{key}}}}}", str(value))

        data = json.dumps(body).encode("utf-8") if body and method in ("POST", "PUT", "PATCH") else None

        req = urllib.request.Request(url, data=data, method=method)
        for header_key, header_value in headers.items():
            req.add_header(header_key, header_value)
        if data:
            req.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_data = response.read().decode("utf-8")
                status_code = response.getcode()
                logger.info(f"HTTP call step completed: {method} {url} -> {status_code}")
                return {
                    "status_code": status_code,
                    "response": response_data[:1000],  # Truncate large responses
                }
        except urllib.error.HTTPError as e:
            logger.error(f"HTTP call step failed: {method} {url} -> {e.code}")
            return {
                "status_code": e.code,
                "error": str(e),
            }
        except urllib.error.URLError as e:
            logger.error(f"HTTP call step URL error: {url} -> {e}")
            raise

    @staticmethod
    @transaction.atomic
    def complete_step(execution, step, result):
        """Mark a step as completed and move to the next.

        Args:
            execution: WorkflowExecution instance
            step: dict with step info
            result: step result data
        """
        WorkflowStepLog.objects.create(
            execution=execution,
            step_name=step.get("name", "unknown"),
            status="completed",
            input_data=step.get("config", {}),
            output_data=result if isinstance(result, dict) else {"result": result},
        )
        logger.info(f"Step '{step.get('name')}' completed for execution {execution.id}")

    @staticmethod
    @transaction.atomic
    def fail_step(execution, step, error):
        """Mark a step as failed.

        Args:
            execution: WorkflowExecution instance
            step: dict with step info
            error: error message string
        """
        WorkflowStepLog.objects.create(
            execution=execution,
            step_name=step.get("name", "unknown"),
            status="failed",
            input_data=step.get("config", {}),
            error_message=str(error),
        )
        execution.status = WorkflowExecutionStatus.FAILED
        execution.save()
        logger.error(
            f"Step '{step.get('name')}' failed for execution {execution.id}: {error}"
        )

    @staticmethod
    def get_execution_status(execution_id):
        """Get the current status of a workflow execution.

        Args:
            execution_id: WorkflowExecution ID

        Returns:
            dict with execution status, current step, and step logs
        """
        try:
            execution = WorkflowExecution.objects.select_related("workflow").get(id=execution_id)
        except WorkflowExecution.DoesNotExist:
            return None

        step_logs = list(
            execution.step_logs.values("step_name", "status", "error_message", "duration_ms", "created_at")
            .order_by("created_at")
        )

        return {
            "execution_id": execution.id,
            "workflow_name": execution.workflow.name,
            "status": execution.get_status_display(),
            "status_code": execution.status,
            "current_step": execution.current_step,
            "total_steps": len(execution.workflow.steps_config) if execution.workflow.steps_config else 0,
            "input_data": execution.input_data,
            "output_data": execution.output_data,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "step_logs": step_logs,
        }

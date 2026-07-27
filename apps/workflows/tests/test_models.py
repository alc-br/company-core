import pytest
from apps.workflows.models import Workflow, WorkflowExecution, WorkflowStepLog


class TestWorkflow:
    def test_workflow_creation(self):
        workflow = Workflow(name="onboarding", steps_config=[{"step": "welcome"}])
        assert workflow.name == "onboarding"

    def test_workflow_execution_creation(self):
        execution = WorkflowExecution(current_step=0)
        assert execution.current_step == 0

    def test_workflow_step_log_creation(self):
        log = WorkflowStepLog(step_name="send_email", status="completed")
        assert log.step_name == "send_email"

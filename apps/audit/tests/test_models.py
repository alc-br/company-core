import pytest
from apps.audit.models import AuditLog


class TestAuditLog:
    def test_audit_log_creation(self):
        log = AuditLog(action="create", target_type="user", target_id="1")
        assert log.action == "create"
        assert log.target_type == "user"

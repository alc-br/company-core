import pytest
from apps.permissions.models import Permission, Role


class TestPermissionModel:
    def test_permission_str(self):
        p = Permission(code="admin_access", name="Admin Access", module="core")
        assert "core.admin_access" in str(p)


class TestRoleModel:
    def test_role_str(self):
        role = Role(name="Admin")
        assert "Admin" in str(role)

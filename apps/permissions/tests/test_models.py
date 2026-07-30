import pytest
from apps.permissions.models import Permission, Role


class TestPermissionModel:
    def test_permission_str(self):
        p = Permission(code="admin_access", name="Admin Access", module="core")
        assert "core.admin_access" in str(p)


class TestRoleModel:
    def test_role_str(self, db):
        from apps.organizations.services import OrganizationService
        from django.contrib.auth import get_user_model
        User = get_user_model()
        owner = User.objects.create_user(email="owner@example.com", password="pass123")
        org = OrganizationService.create_organization(name="Test Org", owner=owner)
        role = Role(name="Admin", organization=org)
        assert "Admin" in str(role)

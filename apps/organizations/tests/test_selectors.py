import pytest
from apps.organizations.selectors import check_user_is_member, get_user_organizations


class TestOrganizationSelectors:
    def test_get_user_organizations_empty(self, db):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(email="user@example.com", password="pass123")
        
        orgs = get_user_organizations(user.id)
        assert orgs.count() == 0

    def test_check_user_is_member_false(self, db):
        assert check_user_is_member(user_id=9999, organization_id=9999) is False

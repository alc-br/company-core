import pytest
from apps.organizations.services import OrganizationService


class TestOrganizationService:
    def test_create_organization(self, db):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(email="owner@example.com", password="pass123")
        
        org = OrganizationService.create_organization(name="Test Org", owner=user)
        assert org.name == "Test Org"
        assert org.owner == user

    def test_invite_member(self, db):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        owner = User.objects.create_user(email="owner@example.com", password="pass123")
        org = OrganizationService.create_organization(name="Test Org", owner=owner)
        
        invitation = OrganizationService.invite_member(
            organization=org,
            email="new@example.com",
            role=2,  # ADMIN
            invited_by=owner,
        )
        assert invitation.email == "new@example.com"
        assert invitation.status == 1  # PENDING

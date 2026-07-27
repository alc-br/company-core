import pytest
from apps.organizations.models import Organization, Membership, Invitation


class TestOrganizationModel:
    def test_organization_str(self):
        org = Organization(name="Test Org")
        assert str(org) == "Test Org"


class TestMembershipModel:
    def test_membership_str(self):
        membership = Membership()
        assert hasattr(membership, "role")
        assert hasattr(membership, "status")


class TestInvitationModel:
    def test_invitation_str(self):
        invitation = Invitation(email="test@example.com")
        assert hasattr(invitation, "token")
        assert hasattr(invitation, "is_expired")

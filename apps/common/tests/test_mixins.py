import pytest
from apps.common.mixins import TimestampMixin, TenantMixin, SoftDeleteMixin


class TestTimestampMixin:
    """Tests for TimestampMixin."""

    def test_has_created_at_field(self):
        assert hasattr(TimestampMixin, "_meta")
        fields = [f.name for f in TimestampMixin._meta.get_fields()]
        assert "created_at" in fields

    def test_has_updated_at_field(self):
        fields = [f.name for f in TimestampMixin._meta.get_fields()]
        assert "updated_at" in fields


class TestTenantMixin:
    """Tests for TenantMixin."""

    def test_has_organization_field(self):
        assert hasattr(TenantMixin, "_meta")
        fields = [f.name for f in TenantMixin._meta.get_fields()]
        assert "organization" in fields


class TestSoftDeleteMixin:
    """Tests for SoftDeleteMixin."""

    def test_has_is_deleted_field(self):
        fields = [f.name for f in SoftDeleteMixin._meta.get_fields()]
        assert "is_deleted" in fields

    def test_has_deleted_at_field(self):
        fields = [f.name for f in SoftDeleteMixin._meta.get_fields()]
        assert "deleted_at" in fields

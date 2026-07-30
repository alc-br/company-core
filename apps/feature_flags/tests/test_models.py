import pytest
from apps.feature_flags.models import FeatureFlag


class TestFeatureFlag:
    def test_str(self):
        flag = FeatureFlag(code="test_flag", name="Test Flag")
        assert "test_flag" in str(flag)

    def test_str_inactive(self):
        flag = FeatureFlag(code="new_feat", name="New Feature", is_active=False)
        assert "OFF" in str(flag)

    def test_str_active(self):
        flag = FeatureFlag(code="active_flag", name="Active", is_active=True)
        assert "ON" in str(flag)

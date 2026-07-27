import pytest
from apps.feature_flags.models import FeatureFlag


class TestFeatureFlag:
    def test_str(self):
        flag = FeatureFlag(name="test_flag")
        assert "test_flag" in str(flag)

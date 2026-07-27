import pytest
from apps.settings.models import TenantSetting, GlobalSetting


class TestTenantSetting:
    def test_tenant_setting_str(self):
        setting = TenantSetting(key="test_key", value="test_value")
        assert "test_key" in str(setting.key)

    def test_global_setting_str(self):
        setting = GlobalSetting(key="global_key", value="global_value")
        assert setting.key == "global_key"

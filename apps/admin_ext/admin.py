from django.contrib import admin

# All models are registered in their respective app admin.py files.
# This module centralizes admin configuration for the Company Core platform.
# Individual apps handle their own ModelAdmin registrations.

# Import all admin modules to trigger their registrations
import apps.organizations.admin  # noqa: F401
import apps.billing.admin  # noqa: F401
import apps.quotas.admin  # noqa: F401
import apps.feature_flags.admin  # noqa: F401
import apps.ai.admin  # noqa: F401
import apps.agents.admin  # noqa: F401
import apps.audit.admin  # noqa: F401
import apps.notifications.admin  # noqa: F401
import apps.webhooks.admin  # noqa: F401
import apps.storage.admin  # noqa: F401
import apps.jobs.admin  # noqa: F401
import apps.usage.admin  # noqa: F401
import apps.analytics.admin  # noqa: F401
import apps.settings.admin  # noqa: F401
import apps.permissions.admin  # noqa: F401
import apps.integrations.admin  # noqa: F401
import apps.workflows.admin  # noqa: F401
import apps.search.admin  # noqa: F401
import apps.api.admin  # noqa: F401
import apps.users.admin  # noqa: F401

from django.contrib import admin
from apps.radar_portal.models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ["title", "organization", "author", "published_at"]
    filter_horizontal = ["clients"]

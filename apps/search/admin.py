from django.contrib import admin
from apps.search.models import SearchIndex


@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    list_display = ("content_type", "object_id", "indexed_at")
    list_filter = ("content_type",)
    search_fields = ("content",)

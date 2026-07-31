from django.contrib import admin
from apps.radar_calendar.models import CalendarEvent, Holiday

admin.site.register(CalendarEvent)
admin.site.register(Holiday)

from django.utils.dateparse import parse_datetime, parse_date
from rest_framework.response import Response

from apps.clients.views import TenantAPIView
from apps.radar_calendar.models import CalendarEvent, Holiday
from apps.radar_tasks.models import Task


def _parse_range(qp):
    start = qp.get("start")
    end = qp.get("end")
    start = parse_datetime(start) or parse_date(start) if start else None
    end = parse_datetime(end) or parse_date(end) if end else None
    return start, end


class CalendarView(TenantAPIView):
    def get(self, request):
        qp = request.query_params
        start, end = _parse_range(qp)
        type_filter = qp.get("type")
        events = []

        if type_filter in (None, "task", "deadline"):
            tasks = Task.objects.filter(organization=request.tenant, due_date__isnull=False).exclude(status=Task.STATUS_CANCELADA)
            if start:
                tasks = tasks.filter(due_date__gte=start)
            if end:
                tasks = tasks.filter(due_date__lte=end)
            for t in tasks.select_related("client")[:500]:
                events.append({
                    "id": f"task-{t.id}",
                    "title": t.title,
                    "startDate": t.due_date,
                    "endDate": None,
                    "allDay": True,
                    "color": None,
                    "type": "deadline" if t.status == Task.STATUS_A_FAZER else "task",
                    "relatedId": t.id,
                    "clientName": t.client.name if t.client_id else None,
                    "status": t.status,
                    "priority": t.priority,
                })

        if type_filter in (None, "meeting", "other"):
            manual = CalendarEvent.objects.filter(organization=request.tenant)
            if start:
                manual = manual.filter(start_date__gte=start)
            if end:
                manual = manual.filter(start_date__lte=end)
            for e in manual.select_related("client"):
                events.append({
                    "id": f"event-{e.id}",
                    "title": e.title,
                    "description": e.description,
                    "startDate": e.start_date,
                    "endDate": e.end_date,
                    "allDay": e.all_day,
                    "color": e.color,
                    "type": e.type,
                    "relatedId": e.id,
                    "clientName": e.client.name if e.client_id else None,
                })

        if type_filter in (None, "holiday"):
            holidays = Holiday.objects.filter(organization=request.tenant)
            for h in holidays:
                if start and h.date < (start.date() if hasattr(start, "date") else start):
                    continue
                if end and h.date > (end.date() if hasattr(end, "date") else end):
                    continue
                events.append({
                    "id": f"holiday-{h.id}",
                    "title": h.name,
                    "startDate": h.date,
                    "endDate": None,
                    "allDay": True,
                    "color": "#6b7280",
                    "type": "holiday",
                    "relatedId": h.id,
                })

        return Response({"events": events})

    def post(self, request):
        data = request.data
        event = CalendarEvent.objects.create(
            organization=request.tenant,
            title=data.get("title", ""),
            description=data.get("description", ""),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            all_day=data.get("all_day", False),
            color=data.get("color", ""),
            type=data.get("type", CalendarEvent.TYPE_MEETING),
            client_id=data.get("client_id"),
        )
        return Response({
            "id": f"event-{event.id}", "title": event.title, "startDate": event.start_date,
            "endDate": event.end_date, "allDay": event.all_day, "type": event.type,
        }, status=201)


class HolidayListCreateView(TenantAPIView):
    def get(self, request):
        holidays = Holiday.objects.filter(organization=request.tenant)
        return Response([{"id": h.id, "name": h.name, "date": h.date, "recurringYearly": h.recurring_yearly} for h in holidays])

    def post(self, request):
        holiday = Holiday.objects.create(
            organization=request.tenant,
            name=request.data.get("name", ""),
            date=request.data.get("date"),
            recurring_yearly=request.data.get("recurring_yearly", False),
        )
        return Response({"id": holiday.id, "name": holiday.name, "date": holiday.date}, status=201)

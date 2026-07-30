"""DRF API ViewSets for notifications app."""

import logging
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.notifications.models import (
    NotificationChannel,
    NotificationTemplate,
    NotificationLog,
)
from apps.notifications.serializers import (
    NotificationChannelSerializer,
    NotificationChannelListSerializer,
    NotificationTemplateSerializer,
    NotificationLogSerializer,
)
from apps.notifications.selectors import (
    get_notification_channel_queryset,
    get_notification_template_queryset,
    get_notification_log_queryset,
)
from apps.notifications.services import NotificationService

logger = logging.getLogger(__name__)

app_name = "notifications"


# ─── Template Views ────────────────────────────────────────────────


@login_required
def list_templates(request):
    templates = NotificationTemplate.objects.all().order_by('code')
    return render(request, 'notifications/list.html', {'templates': templates, 'active_tab': 'templates'})


@login_required
def list_channels(request):
    channels = NotificationChannel.objects.filter(organization=request.tenant).order_by('name') if request.tenant else []
    return render(request, 'notifications/list.html', {'channels': channels, 'active_tab': 'channels'})


# ─── Template CRUD ─────────────────────────────────────────────────


class NotificationTemplateForm(forms.ModelForm):
    class Meta:
        model = NotificationTemplate
        fields = ['code', 'subject', 'body_html', 'body_text', 'channel']


@login_required
def create_template(request):
    if request.method == 'POST':
        form = NotificationTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Template criado com sucesso!")
            return redirect('notifications:list_templates')
    else:
        form = NotificationTemplateForm()
    return render(request, 'notifications/template_form.html', {'form': form})


@login_required
def edit_template(request, pk):
    template = get_object_or_404(NotificationTemplate, pk=pk)
    if request.method == 'POST':
        form = NotificationTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, "Template atualizado com sucesso!")
            return redirect('notifications:list_templates')
    else:
        form = NotificationTemplateForm(instance=template)
    return render(request, 'notifications/template_form.html', {'form': form, 'object': template})


@login_required
def delete_template(request, pk):
    template = get_object_or_404(NotificationTemplate, pk=pk)
    if request.method == 'POST':
        template.delete()
        messages.success(request, "Template excluído com sucesso!")
        return redirect('notifications:list_templates')
    return render(request, 'notifications/template_confirm_delete.html', {
        'object': template,
        'cancel_url': reverse('notifications:list_templates'),
    })


# ─── Channel CRUD ──────────────────────────────────────────────────


class NotificationChannelForm(forms.ModelForm):
    class Meta:
        model = NotificationChannel
        fields = ['type', 'name', 'is_active']


@login_required
def create_channel(request):
    if not request.tenant:
        messages.error(request, "Nenhuma organização selecionada.")
        return redirect('notifications:list_channels')
    if request.method == 'POST':
        form = NotificationChannelForm(request.POST)
        if form.is_valid():
            channel = form.save(commit=False)
            channel.organization = request.tenant
            channel.save()
            messages.success(request, "Canal criado com sucesso!")
            return redirect('notifications:list_channels')
    else:
        form = NotificationChannelForm()
    return render(request, 'notifications/channel_form.html', {'form': form})


@login_required
def edit_channel(request, pk):
    channel = get_object_or_404(NotificationChannel, pk=pk)
    if request.method == 'POST':
        form = NotificationChannelForm(request.POST, instance=channel)
        if form.is_valid():
            form.save()
            messages.success(request, "Canal atualizado com sucesso!")
            return redirect('notifications:list_channels')
    else:
        form = NotificationChannelForm(instance=channel)
    return render(request, 'notifications/channel_form.html', {'form': form, 'object': channel})


@login_required
def delete_channel(request, pk):
    channel = get_object_or_404(NotificationChannel, pk=pk)
    if request.method == 'POST':
        channel.delete()
        messages.success(request, "Canal excluído com sucesso!")
        return redirect('notifications:list_channels')
    return render(request, 'notifications/channel_confirm_delete.html', {
        'object': channel,
        'cancel_url': reverse('notifications:list_channels'),
    })


# ─── DRF API ViewSets ───────────────────────────────────────────────


class NotificationChannelViewSet(viewsets.ModelViewSet):
    """ViewSet for NotificationChannel model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "type", "is_active", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return NotificationChannelListSerializer
        return NotificationChannelSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        if not org_id:
            org_id = self.request.query_params.get("organization_id")
        return get_notification_channel_queryset(organization_id=org_id)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def toggle_active(self, request, pk=None):
        """Toggle the active status of a notification channel."""
        channel = self.get_object()
        channel.is_active = not channel.is_active
        channel.save(update_fields=["is_active"])
        serializer = self.get_serializer(channel)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def test(self, request, pk=None):
        """Send a test notification through this channel."""
        channel = self.get_object()
        recipient = request.data.get("recipient")
        template_code = request.data.get("template_code")
        if not recipient:
            return Response(
                {"error": "recipient field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = NotificationService.send_notification(
                channel="email",
                recipient=recipient,
                template_code=template_code or "test",
            )
            return Response({"status": result})
        except Exception as e:
            logger.exception("Test notification failed")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for NotificationTemplate model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["code", "subject"]
    ordering_fields = ["code", "channel", "created_at"]

    def get_serializer_class(self):
        return NotificationTemplateSerializer

    def get_queryset(self):
        return get_notification_template_queryset(
            channel=self.request.query_params.get("channel"),
            search=self.request.query_params.get("search"),
        )


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for NotificationLog model (read-only)."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["recipient"]
    ordering_fields = ["-created_at", "status", "recipient"]

    def get_serializer_class(self):
        return NotificationLogSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        if not org_id:
            org_id = self.request.query_params.get("organization_id")
        return get_notification_log_queryset(
            organization_id=org_id,
            status=self.request.query_params.get("status"),
            recipient=self.request.query_params.get("recipient"),
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """Get notification statistics."""
        org_id = getattr(request, "tenant", None)
        qs = self.get_queryset()
        from django.db.models import Count
        stats = qs.values("status").annotate(count=Count("id"))
        return Response({"stats": list(stats)})

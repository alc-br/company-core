from apps.clients.models import ClientCompany


def get_client_queryset(organization, search=None, status_filter=None, segment=None, responsible_id=None, tag_id=None):
    qs = ClientCompany.objects.filter(organization=organization, is_deleted=False).select_related("responsible").prefetch_related("tags")

    if search:
        from django.db.models import Q
        qs = qs.filter(Q(name__icontains=search) | Q(trade_name__icontains=search) | Q(cnpj__icontains=search))
    if status_filter:
        qs = qs.filter(status=status_filter)
    if segment:
        qs = qs.filter(segment=segment)
    if responsible_id:
        qs = qs.filter(responsible_id=responsible_id)
    if tag_id:
        qs = qs.filter(tags__id=tag_id)

    return qs.order_by("-created_at")

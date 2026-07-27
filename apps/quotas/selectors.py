def get_all_quotas(organization_id):
    from apps.quotas.models import QuotaAllocation
    return QuotaAllocation.objects.filter(
        organization_id=organization_id
    ).select_related("definition")

def get_quota_definitions():
    from apps.quotas.models import QuotaDefinition
    return QuotaDefinition.objects.all()

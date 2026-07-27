from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.feature_flags.models import FeatureFlag


app_name = "feature_flags"


@login_required
def list_flags(request):
    flags = FeatureFlag.objects.all()
    return render(request, "feature_flags/list.html", {"flags": flags})


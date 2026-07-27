from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


@login_required
def profile_view(request):
    """User profile view."""
    return render(request, "users/profile.html", {"user": request.user})


@login_required
def profile_edit_view(request):
    """User profile edit view."""
    if request.method == "POST":
        form_data = request.POST
        request.user.first_name = form_data.get("first_name", "")
        request.user.last_name = form_data.get("last_name", "")
        request.user.bio = form_data.get("bio", "")
        request.user.timezone = form_data.get("timezone", "America/Sao_Paulo")
        request.user.save()
        return redirect("users:profile")
    return render(request, "users/profile_edit.html", {"user": request.user})

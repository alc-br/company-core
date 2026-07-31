"""JSON auth API used by the Next.js frontend proxy (api/auth/[...path]).

No trailing slashes: the proxy issues requests with `redirect: 'manual'`,
so a slash-appending 301 from Django would be returned verbatim to the
browser instead of being followed.
"""
from django.urls import path
from apps.users import auth_views

urlpatterns = [
    path("api/auth/register", auth_views.api_register, name="api_register"),
    path("api/auth/login", auth_views.api_login, name="api_login"),
    path("api/auth/logout", auth_views.api_logout, name="api_logout"),
]

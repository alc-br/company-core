from django.urls import path
from apps.clients import views

# Sem trailing slash: o proxy do Next.js (redirect: 'manual') nao segue o
# redirect do APPEND_SLASH do Django, entao a rota tem que casar exatamente
# com o path que o frontend chama.
urlpatterns = [
    path("clients", views.ClientListCreateView.as_view()),
    path("clients/<int:pk>", views.ClientDetailView.as_view()),
    path("clients/<int:client_id>/contacts", views.ClientContactListCreateView.as_view()),
    path("client-contacts/<int:pk>", views.ClientContactDetailView.as_view()),
    path("tags", views.TagListCreateView.as_view()),
    path("tags/<int:pk>", views.TagDetailView.as_view()),
    path("departments", views.DepartmentListCreateView.as_view()),
    path("departments/<int:pk>", views.DepartmentDetailView.as_view()),
]

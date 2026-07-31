from django.urls import path
from apps.radar_templates import views

urlpatterns = [
    path("templates", views.TemplateListCreateView.as_view()),
    path("templates/<int:pk>", views.TemplateDetailView.as_view()),
    path("templates/<int:pk>/versions", views.TemplateVersionListView.as_view()),
    path("templates/<int:pk>/publish", views.TemplatePublishView.as_view()),
    path("template-applications", views.TemplateApplicationListCreateView.as_view()),
]

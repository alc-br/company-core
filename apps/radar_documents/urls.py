from django.urls import path
from apps.radar_documents import views

urlpatterns = [
    path("documents", views.DocumentListCreateView.as_view()),
    path("documents/<int:pk>", views.DocumentDetailView.as_view()),
    path("document-types", views.DocumentTypeListCreateView.as_view()),
    path("document-types/<int:pk>", views.DocumentTypeDetailView.as_view()),
    path("document-requests", views.DocumentRequestListCreateView.as_view()),
]

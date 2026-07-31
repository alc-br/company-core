from django.urls import path
from apps.radar_tasks import views

urlpatterns = [
    path("tasks", views.TaskListCreateView.as_view()),
    path("tasks/<int:pk>", views.TaskDetailView.as_view()),
    path("tasks/<int:pk>/comments", views.TaskCommentListCreateView.as_view()),
    path("tasks/<int:pk>/follow", views.TaskFollowView.as_view()),
]

from django.urls import path

from .views import projectviews

app_name = 'productivity'

urlpatterns = [
    path('', projectviews.index, name="index"),
    path('<int:project_id>/', projectviews.projectInfo, name='project_info'),
    path('create/', projectviews.createProject, name='create_project'),
    path('<int:project_id>/delete/', projectviews.deleteProject, name='delete_project'),
    path('sync/', projectviews.sync, name="sync")
]

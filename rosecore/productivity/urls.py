from django.urls import path

from .views import projectviews
from .views import taskviews

app_name = 'productivity'

urlpatterns = [
    path('', projectviews.index, name="index"),
    path('project/create/', projectviews.createProject, name='create_project'),
    path('project/<int:project_id>/', projectviews.projectInfo, name='project_info'),
    path('project/<int:project_id>/delete/', projectviews.deleteProject, name='delete_project'),
    path('project/<int:project_id>/validate/', projectviews.validateProject, name='validate'),
    path('project/<int:project_id>/auto_sync/', projectviews.autoSync, name='auto_sync'),
    path('task/create', taskviews.createTask, name="create_task"),
    path('task/<int:task_id>/', taskviews.taskInfo, name="task_info"),
    path('task/<int:task_id>/delete', taskviews.deleteTask, name="task_delete"),
    path('project/sync/', projectviews.sync, name="sync")
]

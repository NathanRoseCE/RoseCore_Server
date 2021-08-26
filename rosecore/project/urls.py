from django.urls import path

from . import views

app_name = 'project'

urlpatterns = [
    path('', views.index, name="index"),
    path('<int:project_id>/', views.projectInfo, name='project_info'),
    path('create/', views.createProject, name='create_project'),
    path('<int:project_id>/delete/', views.deleteProject, name='delete_project')
]


from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .forms import ProjectForm
from .services import ProjectService
from .exceptions import InvalidProject

# Create your views here.


def index(request):
    project_list = ProjectService.get_projects()
    return render(request, 'project/index.html', {'project_list': project_list})


def projectInfo(request, project_id):
    project = ProjectService.get_project_or_404(project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        error_message = ""
        if form.is_valid():
            form.execute(project_id=project_id)
            return HttpResponseRedirect(reverse('project:index'))
        else:
            error_message += "Form is not valid"
        returnData = {
            'project_id': project_id,
            'form': form,
            'error_message': error_message
        }
    else:
        returnData = {
            'project_id': project_id,
            'form': ProjectForm(instance=project)
        }
    return render(request, 'project/projectInfo.html', returnData)


def createProject(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        error_message = ""
        if form.is_valid():
            form.execute()
            return HttpResponseRedirect(reverse('project:index'))
        else:
            error_message += "Form is not valid"
        returnData = {
            'form': form,
            'error_message': error_message
        }
    else:
        returnData = {
            'form': ProjectForm()
        }
    return render(request, 'project/createProject.html', returnData)

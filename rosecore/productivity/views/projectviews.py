
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from productivity.forms.ProjectForm import ProjectForm
from productivity.services import ProjectService


def index(request):
    project_list = ProjectService.get_root_projects()
    return render(request, 'project/index.html', {'project_list': project_list})


def projectInfo(request, project_id):
    project = ProjectService.get_project_or_404(project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        error_message = ""
        if form.is_valid():
            form.execute(project_id=project_id)
            return HttpResponseRedirect(reverse('productivity:index'))
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
            return HttpResponseRedirect(reverse('productivity:index'))
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


def deleteProject(request, project_id):
    project = ProjectService.get_project_or_404(project_id)
    ProjectService.deleteProject(project)
    return HttpResponseRedirect(reverse('productivity:index'))


def sync(request):
    ProjectService.sync()
    return HttpResponseRedirect(reverse('productivity:index'))

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from productivity.forms.ProjectForm import ProjectForm
from productivity.forms.ProjectMergeForm import ProjectAutoMergeForm
from productivity.services import ProjectService
from productivity.services import TaskService


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
            'project': project,
            'tasks': TaskService.get_tasks_from_project(project),
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

def autoSync(request, project_id):
    unsynced_project = ProjectService.get_project_or_404(project_id)
    if unsynced_project.synced:
        return render(request, 'project/projectInfo.html', {
            "error_message": f"{unsynced_project.name} is already synced!"
        })

    if request.method == 'POST':
        form = ProjectAutoMergeForm(request.POST, unsynced_project=unsynced_project)
        error_message = ""
        if form.is_valid():
            form.execute()
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
            'project': unsynced_project,
            'form': ProjectAutoMergeForm(unsynced_project=unsynced_project)
        }
    return render(request, 'project/merge_with.html', returnData)
        
def validateProject(request, project_id):
    project = ProjectService.get_project_or_404(project_id)
    ProjectService.validate_project(project)
    return HttpResponseRedirect(reverse('productivity:index'))
            

def sync(request):
    ProjectService.sync()
    return HttpResponseRedirect(reverse('productivity:index'))

def nuke_unsynced(request):
    ProjectService.nuke_all_unsynced()
    return HttpResponseRedirect(reverse('productivity:index'))

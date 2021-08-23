
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Project
from .forms import ProjectForm

# Create your views here.


def index(request):
    project_list = Project.objects.all()
    return render(request, 'project/index.html', {'project_list': project_list})


def projectInfo(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'project/projectInfo.html', {'project': project})


def createProject(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            new_project = form.save(commit=False)
            #TODO put id validation here
            new_project.save()
            return HttpResponseRedirect(reverse('project:index'))
        returnData = {
            'form': form,
            'error_message': 'form is not valid'
        }
    else:
        returnData = {
            'form': ProjectForm()
        }
    return render(request, 'project/createProject.html', returnData)

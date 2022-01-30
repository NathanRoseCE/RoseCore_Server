from django.http.response import HttpResponseRedirect
from productivity.services.TaskService import TaskService
from productivity.forms.TaskForm import TaskForm
from django.urls import reverse
from django.shortcuts import render


def taskInfo(request, task_id):
    task = TaskService.get_task_or_404(task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        error_message = ""
        if form.is_valid():
            form.execute(task_id=task_id)
            return HttpResponseRedirect(reverse('productivity:index'))
        else:
            error_message += "Form is not valid"
        returnData = {
            'task_id': task_id,
            'form': form,
            'error_message': error_message
        }
    else:
        returnData = {
            'task_id': task_id,
            'task': task,
            'form': TaskForm(instance=task)
        }
    return render(request, 'task/taskInfo.html', returnData)

def createTask(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
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
            'form': TaskForm()
        }
    return render(request, 'task/createTask.html', returnData)

def deleteTask(request, task_id):
    task = TaskService.get_task_or_404(task_id)
    TaskService.deleteTask(task)
    return HttpResponseRedirect(reverse('productivity:index'))

from django import forms
from django.db.models.query_utils import DeferredAttribute
from productivity import models
from productivity.services.TaskService import TaskService
from productivity.models.Project import Project
import logging

class TaskForm(forms.ModelForm):

    class Meta:
        model = models.Task
        fields = ['content', 'description', 'project', 'priority', 'complete']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = True
        self.fields['project'].required = True
        self.fields['project'].queryset = Project.objects.filter(unsyncedSource="")
    
    def clean_todoistId(self):
        todoistId = self.cleaned_data['todoistId']
        if todoistId != "":
            TaskService.validateTodoistId(todoistId)
        return todoistId

    def execute(self, commit=True, task_id=None):
        args = {
            "content": self.cleaned_data['content']
        }
        if "todoistId" in self.cleaned_data:
            args["todoistId"] = self.cleaned_data['todoistId']
        args["description"] = self.cleaned_data['description']
        args["project"] = self.cleaned_data['project']
        args["priority"] = self.cleaned_data['priority']
        args["complete"] = self.cleaned_data['complete']
        if task_id is None:
            print(args)
            TaskService.createTask(**args)
        else:
            task = self.instance
            task.content = args["content"]
            task.description = args["description"]
            task.priority = args["priority"]
            TaskService.updateTask(task)

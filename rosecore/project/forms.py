from django import forms
from . import models
from .services import ProjectService
from .exceptions import InvalidProject
from django.core.exceptions import ValidationError

class ProjectForm(forms.ModelForm):

    class Meta:
        model = models.Project
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True

    def clean_togglId(self):
        togglId = self.cleaned_data['togglId']
        if togglId != "":
            try:
                ProjectService.validateTogglId(togglId)
            except InvalidProject:
                    raise ValidationError(
                        f'Invalid todoistId: {togglId}'
                    )
        return togglId
    
    def clean_todoistId(self):
        todoistId = self.cleaned_data['todoistId']
        if todoistId != "":
            try:
                ProjectService.validateTogglId(todoistId)
            except InvalidProject:
                    raise ValidationError(
                        f'Invalid todoistId: {todoistId}',
                    )
            ProjectService.validateTogglId(todoistId)
        return todoistId

    def execute(self, commit=True, project_id=None):
        args = {
            "name": self.cleaned_data['name']
        }
        if "togglId" in self.cleaned_data:
            args["togglId"] = self.cleaned_data['togglId']
        if "todoistId" in self.cleaned_data:
            args["todoistId"] = self.cleaned_data['todoistId']

        if project_id is None:
            ProjectService.createProject(**args)
        else:
            project = self.instance
            project.name = args["name"]
            ProjectService.updateProject(project)

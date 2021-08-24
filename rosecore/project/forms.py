from django import forms
from . import models
from .services import ProjectService


class ProjectForm(forms.ModelForm):

    class Meta:
        model = models.Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['togglId'].required = False
        self.fields['todoistId'].required = False

    def clean_togglId(self):
        togglId = self.cleaned_data['togglId']
        if togglId != "":
            ProjectService.validateTogglId(togglId)
        return togglId
    
    def clean_todoistId(self):
        todoistId = self.cleaned_data['todoistId']
        if todoistId != "":
            ProjectService.validateTogglId(todoistId)
        return todoistId
        
    def execute(self):
        ProjectService.createProject(
            name=self.cleaned_data['name'],
            togglId=self.cleaned_data['togglId'],
            todoistId=self.cleaned_data['todoistId']
        )

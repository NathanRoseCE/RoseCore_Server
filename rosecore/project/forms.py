from django import forms
from . import models


class ProjectForm(forms.ModelForm):
    togglId = forms.CharField(label="Toggl Id", max_length=20, required=False)
    todoistId = forms.CharField(label="Todoist Id", max_length=20, required=False)

    class Meta:
        model = models.Project
        fields = '__all__'

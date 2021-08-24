from django import forms
from . import models


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['togglId'].required = True
        self.fields['todoistId'].required = True

    class Meta:
        model = models.Project
        fields = '__all__'


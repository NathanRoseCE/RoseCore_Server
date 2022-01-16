from django import forms
from productivity.services.ProjectService import ProjectService
from productivity.models.Project import Project
from django.core.exceptions import ValidationError

class ProjectAutoMergeForm(forms.Form):
    merge_with = forms.ModelChoiceField(
        empty_label="Choose a project to merge with",
        queryset=ProjectService.synced_queryset()
    )

    def __init__(self, *args, **kwargs) -> None:
        self._unsynced_project = kwargs["unsynced_project"]
        del kwargs["unsynced_project"]
        super().__init__(*args, **kwargs)

    def execute(self) -> None:
        if self._unsynced_project.synced:
            raise ValidationError(
                f"{self._unsynced_project.name} project is already synced!"
            )
        ProjectService.merge_synced_and_unsynced(
            synced_project=self.cleaned_data["merge_with"],
            unsynced_project=self._unsynced_project
        )

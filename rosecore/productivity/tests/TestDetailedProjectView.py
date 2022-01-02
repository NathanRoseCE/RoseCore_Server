from django.test import TestCase
from productivity.models.Project import Project
from django.urls import reverse

class ProjectDetailedViewTests(TestCase):
    def test_view_project(self):
        project = Project.objects.create(name="testThree")
        response = self.client.get(reverse("productivity:project_info", args=(project.id,)))
        self.assertContains(response, project.name)

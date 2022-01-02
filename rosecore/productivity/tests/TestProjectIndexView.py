from django.test import TestCase
from django.urls import reverse
from productivity.models.Project import Project

class ProjectIndexViewTests(TestCase):
    def test_no_projects(self):
        response = self.client.get(reverse("productivity:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Its empty here, want to create a project?")

    def test_projects_viewable(self):
        projectOne = Project.objects.create(name="test")
        projectTwo = Project.objects.create(name="testTwo")
        response = self.client.get(reverse("productivity:index"))
        self.assertContains(
            response,
            projectOne
        )
        self.assertContains(
            response,
            projectTwo
        )


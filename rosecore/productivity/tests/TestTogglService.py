from productivity.services.TogglService import TogglService
from django.conf import settings
from django.test import TestCase


class TogglServiceTest(TestCase):
    def setUp(self):
        self.wid = settings.TOGGL_WORKSPACE_ID
        self.togglId = settings.TOGGL_ID

    def test_createProjectAndDelete(self):
        testName = "test"
        newId = TogglService.createProject(name=testName)
        self.assertEqual(
            str(newId), TogglService.getProject(newId)["id"]
        )
        self.assertEqual(
            True, str(newId) in [project["id"] for project in TogglService.getAllProjects()]
        )
        project = TogglService.getProject(newId)
        self.assertEqual(
            testName, project["name"]
        )
        testName = "newName"
        project["name"] = testName
        TogglService.updateProject(project)
        project = TogglService.getProject(newId)
        self.assertEqual(
            testName, project["name"]
        )

        TogglService.deleteProject(newId)
        self.assertEqual(
            False, newId in [project["id"] for project in TogglService.getAllProjects()]
        )

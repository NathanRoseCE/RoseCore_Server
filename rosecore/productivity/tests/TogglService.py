from django.test import TestCase
from productivity.services.TogglService import TogglService
from django.conf import settings


class TogglServiceTest(TestCase):
    testProjects = []

    def setUp(self):
        self.wid = settings.TOGGL_WORKSPACE_ID
        self.togglId = settings.TOGGL_ID

    def tearDown(self):
        for project in TogglServiceTest.testProjects:
            TogglService.deleteProject(project)

    def test_createProjectAndDelete(self):
        testName = "test"
        newId = TogglService.createProject(name=testName)
        TogglServiceTest.testProjects.append(newId)
        self.assertEqual(
            newId, TogglService.getProject(newId)["id"]
        )
        self.assertEqual(
            True, newId in [project["id"] for project in TogglService.getAllProjects()]
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

        TogglService.deleteProject(id=newId)
        self.assertEqual(
            False, newId in [project["id"] for project in TogglService.getAllProjects()]
        )

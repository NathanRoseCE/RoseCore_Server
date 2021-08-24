from django.test import TestCase
from django.core.validators import ValidationError
from django.conf import settings
from todoist.api import TodoistAPI

from .models import Project
from .services import ProjectService, TodoistService, TogglService
from .exceptions import InvalidProject


class ProjectTest(TestCase):
    def test_todoist_id_required(self):
        p = Project(name="test", togglId="someVal")
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_toggl_id_required(self):
        p = Project(name="test", todoistId="someVal")
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_name_required(self):
        p = Project(togglId="test", todoistId="someVal")
        with self.assertRaises(ValidationError):
            p.full_clean()


class ProjectServiceTest(TestCase):
    def setUp(self):
        self.projectOne = Project(name="test_one", togglId="testIdOne", todoistId="testIdOne")
        self.projectTwo = Project(name="test_two", togglId="testIdTwo", todoistId="testIdTwo")
        self.projectOne.save()
        self.projectTwo.save()
        self.deleteProjects = []

    def tearDown(self):
        self.projectOne.delete()
        self.projectTwo.delete()
        for project in self.deleteProjects:
            if project.todoistId != "":
                TodoistService.deleteProject(project.todoistId)
            if project.togglId != "":
                TogglService.deleteProject(project.togglId)
            project.delete()

    def test_get_projects(self):
        projects = ProjectService.get_projects(limit=1)
        self.assertEqual(
            (self.projectOne in projects) or (self.projectTwo in projects),
            True
        )
        self.assertEqual(
            (self.projectOne in projects) and (self.projectTwo in projects),
            False
        )

    def test_create_with_invalid_todoist_id(self):
        with self.assertRaises(InvalidProject):
            ProjectService.createProject(name="Test Project", todoistId="invalid")

    def test_create_with_invalid_toggl_id(self):
        with self.assertRaises(InvalidProject):
            ProjectService.createProject(name="Test Project", togglId="invalid")

    def test_create_project_creates_in_todoist(self):
        project = ProjectService.createProject("Test Project_Todoist_id")
        self.deleteProjects.append(project)
        todoistProject = TodoistService.getProject(id=project.todoistId)
        self.assertEqual(project.todoistId, todoistProject["id"])
        self.assertEqual(project.name, todoistProject["name"])

    def test_create_project_creates_in_toggl(self):
        project = ProjectService.createProject("Test Project_toggl_id")
        self.deleteProjects.append(project)
        togglProject = TogglService.getProject(id=project.togglId)
        self.assertEqual(project.togglId, togglProject["id"])
        self.assertEqual(project.name, togglProject["name"])

    def test_noIdMatch(self):
        todoistProjects = [
            {
                "id": "testIdOne",
                "name": "test_one",
                "parent_id": None,
                "archived": False
            },{
                "id": "testIdTwo",
                "name": "test_two_wrong",
                "parent_id": None,
                "archived": False
            },{
                "id": "testIdThree",
                "name": "test_three_wrong",
                "parent_id": None,
                "archived": False
            }
        ]
        togglProjects = [
            {
                "id": "testIdOne",
                "name": "test_one",
                "parent_id": None,
                "archived": False
            },{
                "id": "testIdTwo",
                "name": "test_two_wrong",
                "parent_id": None,
                "archived": False
            },{
                "id": "testIdThree",
                "name": "test_three_wrong",
                "parent_id": None,
                "archived": False
            }
        ]
        results = ProjectService._nonIdMatch(todoistProjects.copy(), togglProjects.copy())

        self.assertEqual(todoistProjects[1] in results["todoist"]["update"], True)
        self.assertEqual(len(results["todoist"]["update"]), 1)
        self.assertEqual(todoistProjects[2] in results["todoist"]["delete"], True)
        self.assertEqual(len(results["todoist"]["delete"]), 1)

        self.assertEqual(todoistProjects[1] in results["toggl"]["update"], True)
        self.assertEqual(len(results["toggl"]["update"]), 1)
        self.assertEqual(todoistProjects[2] in results["toggl"]["delete"], True)
        self.assertEqual(len(results["toggl"]["delete"]), 1)


class TodoistServiceTest(TestCase):
    def setUp(self):
        self.api = TodoistAPI(settings.TODOIST_KEY)
        for project in self.api.state['projects']:
            project.delete()
        self.api.commit()

    def tearDown(self):
        self.api.sync()
        for project in self.api.state['projects']:
            project.delete()
        self.api.commit()

    def test_create_project(self):
        name = "testName"
        someId = TodoistService.createProject(name=name)
        self.api.sync()
        self.assertEqual(
            name in [project.data["name"] for project in self.api.state['projects']],
            True
        )
        matchingProject = [project for project in self.api.state['projects'] if project.data["name"] == name][0]

        self.assertEqual(
            str(matchingProject.data["id"]),
            someId
        )

    def test_update_project(self):
        name = "testName"
        someId = TodoistService.createProject(name=name)
        self.api.sync()
        self.assertEqual(
            name in [project.data["name"] for project in self.api.state['projects']],
            True
        )
        matchingProject = [project for project in self.api.state['projects'] if project.data["name"] == name][0]
        self.assertEqual(
            str(matchingProject.data["id"]),
            someId
        )
        name = "testNameTwo"
        matchingProject["name"] = name
        TodoistService.updateProject(data=matchingProject)
        matchingProject = [project for project in self.api.state['projects'] if project.data["name"] == name][0]
        self.assertEqual(
            str(matchingProject.data["id"]),
            someId
        )

    def test_delete_project(self):
        project = self.api.projects.add("test")
        self.api.commit()
        TodoistService.deleteProject(id=project.data["id"])
        self.api.sync()
        self.assertEqual(
            self.api.projects.get_by_id(project.data["id"]),
            None
        )

    def test_get_project_by_id(self):
        correct = self.api.projects.add("test")
        self.api.commit()
        actual = TodoistService.getProject(correct.data["id"])
        self.assertEqual(str(correct.data["id"]), actual["id"])
        self.assertEqual(correct.data["name"], actual["name"])
        self.assertEqual(correct.data["parent_id"], actual["parent_id"])
        self.assertEqual(correct.data["is_archived"] == 1, actual["archived"])

    def test_get_projects(self):
        self.api.projects.add("testOne")
        self.api.projects.add("testTwo")
        self.api.commit()
        self.api.sync()
        TodoistService.sync()
        for local in self.api.state["projects"]:
            self.assertEqual(
                str(local.data["id"]) in [remote["id"] for remote in TodoistService.getAllProjects()],
                True
            )
            match = [project for project in TodoistService.getAllProjects() if str(local.data["id"]) == project["id"]][0]
            self.assertEqual(
                local.data["name"], match["name"]
            )
            parent_id = str(local.data["parent_id"]) if local.data["parent_id"] is not None else None
            self.assertEqual(
                parent_id, match["parent_id"]
            )
            self.assertEqual(
                local.data["is_archived"] == 1, match["archived"]
            )


class TogglServiceTest(TestCase):
    def setUp(self):
        self.wid = settings.TOGGL_WORKSPACE_ID
        self.togglId = settings.TOGGL_ID

    def test_createProjectAndDelete(self):
        testName = "test"
        newId = TogglService.createProject(name=testName)
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

from django.test import TestCase
from django.core.validators import ValidationError
from http import HTTPStatus
from django.conf import settings

from todoist.api import TodoistAPI

from .models import Project
from .services import ProjectService, TodoistService
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
        self.projectOne = Project(name="test", togglId="testId", todoistId="testId2")
        self.projectTwo = Project(name="teste", togglId="testId", todoistId="testId2")
        self.projectOne.save()
        self.projectTwo.save()

    def tearDown(self):
        self.projectOne.delete()
        self.projectTwo.delete()

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
        project = ProjectService.createProject("Test Project")
        todoistProject = TodoistService.getProject(id=project.todoistId)
        self.assertEqual(project.todoistId, todoistProject["id"])


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

        

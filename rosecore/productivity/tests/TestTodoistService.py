from todoist.api import TodoistAPI
from django.test import TestCase
from django.conf import settings
from productivity.services.TodoistService import TodoistService
import unittest

class TodoistServiceTest(TestCase):
    def setUp(self):
        [TodoistService.deleteTask(task["id"]) for task in TodoistService.getAllTasks()]

    def tearDown(self):
        [TodoistService.deleteTask(task["id"]) for task in TodoistService.getAllTasks()]

    def test_CRUD_project(self):
        name = "testName"
        someId = TodoistService.createProject(name=name)
        self.assertEqual(
            name in [project["name"] for project in TodoistService.getAllProjects()],
            True
        )
        matchingProject = [project for project in TodoistService.getAllProjects() if project["name"] == name][0]

        self.assertEqual(
            str(matchingProject["id"]),
            someId
        )
        
        new_name = "testNameTwo"
        matchingProject["name"] = new_name
        TodoistService.updateProject(data=matchingProject)
        self.assertEqual(
            new_name in [project["name"] for project in TodoistService.getAllProjects()],
            True
        )
        matchingProject = [
            project for project in TodoistService.getAllProjects() if project["name"] == new_name
        ][0]
        self.assertEqual(
            str(matchingProject["id"]),
            someId
        )
        TodoistService.deleteProject(id=matchingProject["id"])
        self.assertTrue(
            new_name not in [project["name"] for project in TodoistService.getAllProjects()],
        )

    @unittest.skip("Bug in todoist api, bug reported")
    def test_CRUD_task(self):
        content = "test content"
        due_string="today"
        pid = TodoistService.createProject("test_project")
        task_id = TodoistService.createTask(
            content=content,
            due_string=due_string,
            project_id=pid
        )
        self.assertEqual(
            content in [task["content"] for task in TodoistService.getAllTasks()],
            True
        )
        matchingTask = [
            task for task in TodoistService.getAllTasks() if task["content"] == content
        ][0]

        self.assertEqual(
            str(matchingTask["id"]),
            task_id
        )
        self.assertEqual(
            matchingTask["project_id"],
            pid
        )

        new_content = "test update"
        new_description = "test description"
        TodoistService.updateTask({
            "content": new_content,
            "description": new_description
        })
        self.assertTrue(
            new_content in [task["content"] for task in TodoistService.getAllTasks()]
        )
        self.assertEqual(
            matchingTask["project_id"],
            pid
        )
        matchingTask = [
            task for task in TodoistService.getAllTasks() if task["content"] == content
        ][0]
        self.assertEqual(matchingTask["content"], new_content)
        self.assertEqual(matchingTask["description"], new_description)
        self.assertEqual(matchingTask["project_id"], pid)
        self.assertEqual(matchingTask["id"], task_id)

        TodoistService.deleteTask(task_id)
        self.assertFalse(
            new_content in [task["content"] for task in TodoistService.getAllTasks()]
        )
        

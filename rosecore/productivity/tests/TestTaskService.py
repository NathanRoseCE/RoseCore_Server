from django.test import TestCase
from productivity.services.TaskService import TaskService
from productivity.services.ProjectService import ProjectService
import unittest

class TestTaskService(TestCase):

    @unittest.skip("Bug in todoist api")
    def test_CRUD_task(self) -> None:
        project = ProjectService.createProject(
            "test task project"
        )
        content = "test CRUS TaskService"
        desc = "test CRUD desc"
        priority = 2
        task = TaskService.createTask(
            content = content,
            description = desc,
            project=project,
            priority=priority
        )
        task = TaskService.getTask(task.id)
        self.assertEqual(task.content, content)
        self.assertEqual(task.project, project)
        self.assertEqual(task.description, desc)
        self.assertEqual(task.priority, priority)

        new_content = "test CRUD updated"
        new_priority = 4
        new_project = ProjectService.createProject(
            "test new CRDU project"
        )
        task.content = new_content
        task.priority = new_priority
        task.project = new_project
        TaskService.updateTask(task)
        task = TaskService.getTask(task.id)
        self.assertEqual(task.content, content)
        self.assertEqual(task.project, project)
        self.assertEqual(task.description, desc)
        self.assertEqual(task.priority, priority)

        TaskService.deleteTask(task)
        self.assertFalse(
            task.id in [task.id for task in TaskService.get_tasks()]
        )

    def test_get_mark_complate(self) -> None:
        pass

    def test_todoist_persistance(self) -> None:
        pass

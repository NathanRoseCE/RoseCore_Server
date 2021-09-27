from django.test import TestCase
from productivity.models.Task import Task
from django.core.validators import ValidationError
from productivity.models.Project import Project
from datetime import datetime


class TaskTest(TestCase):
    def test_todoistid_required(self):
        project = Project(name="project_test_prio_min", togglId="parentId", todoistId="parentId")
        project.save()
        task = Task(content="some string",
                    project=project,
                    due=datetime(2015, 10, 9, 23, 55, 59, 342380))
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_priority_min(self):
        project = Project(name="project_test_prio_min", togglId="parentId", todoistId="parentId")
        project.save()
        task = Task(content="some string", todoistId="asd", priority=10,
                    project=project,
                    due=datetime(2015, 10, 9, 23, 55, 59, 342380))
        task = Task(content="some string", todoistId="asd", priority=-10)
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_priority_max(self):
        project = Project(name="project_test_prio_max", togglId="parentId", todoistId="parentId")
        project.save()
        task = Task(content="some string", todoistId="asd", priority=10,
                    project=project,
                    due=datetime(2015, 10, 9, 23, 55, 59, 342380))
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_priority_values(self):
        project = Project(name="project_test_prio_vals", togglId="parentId", todoistId="parentId")
        project.save()
        for i in range(1, 4):
            task = Task(content="some string", todoistId="asd", priority=i,
                        project=project,
                        due=datetime(2015, 10, 9, 23, 55, 59, 342380))
            try:
                task.full_clean()
            except ValidationError:
                self.fail("Valid priority marked as invalid: " + str(i))

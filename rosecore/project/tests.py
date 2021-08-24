from django.test import TestCase
from django.core.validators import ValidationError
from http import HTTPStatus
# Create your tests here.

from .models import Project


class QuestionModelTests(TestCase):
    def test_project_creation_normal(self):
        response = self.client.post(
            "/project/create/", data={"name": "TestProject"}
        )
        self.assertEqual(response.status_code, 200)

        
class PersonTest(TestCase):
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

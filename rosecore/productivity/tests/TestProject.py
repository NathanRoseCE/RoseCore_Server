from django.test import TestCase
from productivity.models.Project import Project
from django.core.validators import ValidationError

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

    def test_parent_relationship(self):
        parent=Project(name="parent", togglId="parentId", todoistId="parentId")
        child=Project(name="child", togglId="parentId", todoistId="parentId", parent=parent)
        parent.save()
        child.save()
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())
        child.delete()
        parent.delete()



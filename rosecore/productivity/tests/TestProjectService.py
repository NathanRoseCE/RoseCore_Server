from productivity.models.Project import Project
from django.test import TestCase
from productivity.services.ProjectService import ProjectService
from productivity.utilities.exceptions import InvalidProject
from productivity.services.TodoistService import TodoistService
from productivity.services.TogglService import TogglService

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
            try:
                if project.todoistId != "":
                    TodoistService.deleteProject(project.todoistId)
                if project.togglId != "":
                    TogglService.deleteProject(project.togglId)
                project.delete()
            except Exception:
                pass

    def test_root_project_service(self):
        childOne = Project(name="test_child", togglId="assdf", todoistId="sfffdsafafds", parent=self.projectOne)
        childTwo = Project(name="test_childTwo", togglId="asdsaf", todoistId="safdfdjsklas", parent=self.projectTwo)
        childOne.save()
        childTwo.save()
        roots = ProjectService.get_root_projects()
        self.assertIn(self.projectOne, roots)
        self.assertIn(self.projectTwo, roots)
        self.assertNotIn(childOne, roots)
        self.assertNotIn(childTwo, roots)

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
        self.assertEqual(project.togglId, str(togglProject["id"]))
        self.assertEqual(project.name, togglProject["name"])

    def test_delete_project(self):
        project = ProjectService.createProject("Test Project_delete")
        id = project.id
        todoistId = project.todoistId
        togglId = project.togglId
        ProjectService.deleteProject(project)
        self.assertEqual(False, id in [project.id for project in Project.objects.all()])
        self.assertEqual(False, todoistId in [project["id"] for project in TodoistService.getAllProjects()])
        self.assertEqual(False, togglId in [project["id"] for project in TogglService.getAllProjects()])

class ProjectServiceSyncTest(TestCase):
    def test_ensure_client_projects_present(self):
        synced_project = ProjectService.createProject("test_synced")
        test_project = Project(name="test_unsynced")
        test_project.save()
        self.assertFalse(test_project.name in [todoist_project["name"]
                                               for todoist_project in TodoistService.getAllProjects()])
        self.assertTrue(synced_project.name in [todoist_project["name"]
                                               for todoist_project in TodoistService.getAllProjects()])
        ProjectService.sync()
        self.assertTrue(test_project.name in [todoist_project["name"]
                                              for todoist_project in TodoistService.getAllProjects()])
        self.assertTrue(synced_project.name in [todoist_project["name"]
                                               for todoist_project in TodoistService.getAllProjects()])

    def test_unsynced_todoist_project(self):
        todoist_project_name = "todoist_unsyced"
        TodoistService.createProject(name=todoist_project_name)
        todoist_project = [project for project in TodoistService.getAllProjects()
                           if project["name"] == todoist_project_name][0]
        self.assertFalse(todoist_project["name"] in [project.name for project in ProjectService.get_projects()])

        ProjectService.sync()
        self.assertTrue(todoist_project["name"] in [project.name for project in ProjectService.get_projects()])
        unsynced_project = [project for project in ProjectService.get_projects()
                            if project.name == todoist_project_name][0]
        self.assertFalse(unsynced_project.synced)
        self.assertTrue("todoist" in unsynced_project.unsyncedSource)
        
        

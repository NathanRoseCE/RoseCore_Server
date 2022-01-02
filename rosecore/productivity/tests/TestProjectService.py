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
            if project.todoistId != "":
                TodoistService.deleteProject(project.todoistId)
            if project.togglId != "":
                TogglService.deleteProject(project.togglId)
            try:
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
        self.assertEqual(project.togglId, int(togglProject["id"]))
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
        projects = Project.objects.all()
        results = ProjectService._nonIdMatch(projects, todoistProjects.copy(), togglProjects.copy())

        self.assertEqual(todoistProjects[1] in results["todoist"]["update"], True)
        self.assertEqual(len(results["todoist"]["update"]), 1)
        self.assertEqual(todoistProjects[2] in results["todoist"]["delete"], True)
        self.assertEqual(len(results["todoist"]["delete"]), 1)

        self.assertEqual(todoistProjects[1] in results["toggl"]["update"], True)
        self.assertEqual(len(results["toggl"]["update"]), 1)
        self.assertEqual(todoistProjects[2] in results["toggl"]["delete"], True)
        self.assertEqual(len(results["toggl"]["delete"]), 1)

    def test_nameMatch(self):
        projects = [
            Project(
                name="test name match one",
                todoistId="123",
                togglId="342",
            ),
            Project(
                name="test name match two",
                todoistId="124",
                togglId="3433",
             )
        ]
        idResults = {
            "todoist": {
                "delete": [
                    {
                        "name": "test name match one",
                        "id": "correctTodoistIdOne"
                    },
                    {
                        "name": "deleteThisStill",
                        "id": "dafdsaljkl"
                    }
                ],
                "update":[]
            },
            "toggl": {
                "delete": [
                    {
                        "name": "test name match one",
                        "id": "correctTogglIdOne"
                    },
                    {
                        "name": "deleteThisStill",
                        "id": "fljakl;fjds"
                    }
                ],
                "update":[]
            }
        }
        results = ProjectService._parseForNameMatches(projects, idResults)
        self.assertEqual(
            projects[0].todoistId, "correctTodoistIdOne"
        )
        self.assertEqual(
            projects[0].togglId, "correctTogglIdOne"
        )
        self.assertEqual(
            "test name match one" in [project["name"] for project in results["todoist"]["update"]],
            True
        )
        self.assertEqual(
            "test name match one" in [project["name"] for project in results["toggl"]["update"]],
            True
        )
        self.assertEqual(
            "test name match one" in [project["name"] for project in results["todoist"]["delete"]],
            False
        )
        self.assertEqual(
            "test name match one" in [project["name"] for project in results["toggl"]["delete"]],
            False
        )
        # ---
        self.assertEqual(
            "deleteThisStill" in [project["name"] for project in results["todoist"]["update"]],
            False
        )
        self.assertEqual(
            "deleteThisStill" in [project["name"] for project in results["todoist"]["delete"]],
            True
        )
        self.assertEqual(
            "deleteThisStill" in [project["name"] for project in results["toggl"]["update"]],
            False
        )
        self.assertEqual(
            "deleteThisStill" in [project["name"] for project in results["toggl"]["delete"]],
            True
        )



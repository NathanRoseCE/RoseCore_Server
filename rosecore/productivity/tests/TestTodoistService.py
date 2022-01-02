from todoist.api import TodoistAPI
from django.test import TestCase
from django.conf import settings
from productivity.services.TodoistService import TodoistService


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

    # def test_get_projects(self):
    #     self.api.projects.add("testOne")
    #     self.api.projects.add("testTwo")
    #     self.api.commit()
    #     self.api.sync()
    #     TodoistService.sync()
    #     for local in self.api.state["projects"]:
    #         self.assertTrue(
    #             str(local.data["id"]) in 
    #             [str(remote["id"]) for remote in TodoistService.getAllProjects()]
    #         )
    #         match = [project for project in TodoistService.getAllProjects() if str(local.data["id"]) == project["id"]][0]
    #         self.assertEqual(
    #             local.data["name"], match["name"]
    #         )
    #         parent_id = str(local.data["parent_id"]) if local.data["parent_id"] is not None else None
    #         self.assertEqual(
    #             parent_id, match["parent_id"]
    #         )
    #         self.assertEqual(
    #             local.data["is_archived"] == 1, match["archived"]
    #         )

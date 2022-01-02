"""
 tests for django, offline tests only by default, unless
 API_ENDPOINT_TESTS is set and true
"""
from django.test import TestCase
from django.conf import settings
from productivity.libs.Toggl.TogglTrack import TogglTrack
from productivity.libs.Toggl.Project import Project


class LocalTogglProjectTester(TestCase):
    def setUp(self):
        wid = settings.TOGGL_WORKSPACE_ID
        togglId = settings.TOGGL_ID
        toggl = TogglTrack(wid, togglId)
        toggl.sync()
        for project in toggl.projects:
            toggl.deleteProject(project)
        toggl.sync()
        
    def test_create_project(self):
        toggl = TogglTrack(-1, -1, False)
        projectName = "test project"
        toggl.createProject(projectName)
        self.assertTrue(
            projectName in
            [project.name for project in toggl.projects]
        )
    
    def test_delete_project(self):
        toggl = TogglTrack(-1, -1, False)
        projectName = "test project"
        project = toggl.createProject(projectName)
        self.assertTrue(
            projectName in
            [project.name for project in toggl.projects]
        )
        toggl.deleteProject(project)
        self.assertFalse(
            projectName in
            [project.name for project in toggl.projects]

        )

    def test_update_project_name(self):
        toggl = TogglTrack(-1, -1, False)
        oldProjectName = "old project name"
        newProjectName = "test project"
        project = toggl.createProject(oldProjectName)
        toggl.updateProject(project, newProjectName)
        self.assertTrue(
            newProjectName in
            [project.name for project in toggl.projects]
        )
        self.assertFalse(
            oldProjectName in
            [project.name for project in toggl.projects]
        )

    def test_project_syncing(self):
        wid = settings.TOGGL_WORKSPACE_ID
        togglId = settings.TOGGL_ID
        toggl = TogglTrack(wid, togglId)
        togglTwo = TogglTrack(wid, togglId)
        original_name = "test_project"
        project = toggl.createProject(original_name)
        toggl.sync()
        togglTwo.sync()
        self.assertTrue(
            original_name in
            [remoteProject.name for remoteProject in togglTwo.projects]
        )
        project = [r_project for r_project in toggl.projects if r_project.name == original_name][0]
        newName = "test New Name"
        toggl.updateProject(project, newName)
        toggl.sync()
        togglTwo.sync()
        self.assertTrue(
            newName in
            [remoteProject.name for remoteProject in togglTwo.projects]
        )
        self.assertFalse(
            original_name in
            [remoteProject.name for remoteProject in togglTwo.projects]
        )
        project = [r_project for r_project in toggl.projects if r_project.name == newName][0]
        
        toggl.deleteProject(project)
        toggl.sync()
        togglTwo.sync()
        self.assertFalse(
            newName in
            [remoteProject.name for remoteProject in togglTwo.projects]
        )        

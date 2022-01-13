"""
 tests for django, offline tests only by default, unless
 API_ENDPOINT_TESTS is set and true
"""
from django.test import TestCase
from django.conf import settings
from productivity.libs.Toggl.TogglTrack import TogglTrack
from productivity.libs.Toggl.Project import Project
from datetime import datetime, timedelta
import datetime as dt
import time
import pytz

class LocalTogglProjectTester(TestCase):
    def test_create_project(self):
        toggl = TogglTrack(-1, -1, allowSync=False)
        projectName = "test project"
        toggl.createProject(projectName)
        self.assertTrue(
            projectName in
            [project.name for project in toggl.projects]
        )
    
    def test_delete_project(self):
        toggl = TogglTrack(-1, -1, allowSync=False)
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
        toggl = TogglTrack(-1, -1, allowSync=False)
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
        toggl.sync()
        for project in toggl.projects:
            toggl.deleteProject(project)
        toggl.sync()
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


class LocalTogglTimeEntryTester(TestCase):
    def test_create_time_entry(self):
        toggl = TogglTrack(-1, -1, False)
        project_id = 3
        description = "Test time entry"
        tags = [
            "one",
            "two"
        ]
        toggl.create_time_entry(project_id,description,tags)
        self.assertTrue(
            description in
            [entry.description for entry in toggl.time_entries]
        )
        entry = [entry for entry in toggl.time_entries if entry.description == description][0]
        self.assertEqual(
            entry.project_id,
            project_id
        )
        for tag in tags:
            self.assertTrue(
                tag in entry.tags
            )
    
    def test_delete_time_entry(self):
        toggl = TogglTrack(-1, -1, False)
        project_id = 3
        description = "Test time entry"
        tags = [
            "one",
            "two"
        ]
        time_entry = toggl.create_time_entry(project_id,description,tags)
        self.assertTrue(
            description in
            [entry.description for entry in toggl.time_entries]
        )
        toggl.delete_time_entry(time_entry)
        self.assertFalse(
            description in
            [entry.description for entry in toggl.time_entries]
        )

    def test_update_time_entry_description(self):
        toggl = TogglTrack(-1, -1, False)
        project_id = 3
        description = "Test time entry"
        tags = [
            "one",
            "two"
        ]
        time_entry = toggl.create_time_entry(project_id,description,tags)
        self.assertTrue(
            description in
            [entry.description for entry in toggl.time_entries]
        )
        new_description = "new time entry"
        toggl.update_time_entry(time_entry, description=new_description)
        self.assertFalse(
            description in
            [entry.description for entry in toggl.time_entries]
        )
        self.assertTrue(
            new_description in
            [entry.description for entry in toggl.time_entries]
        )

        time_entry = [entry for entry in toggl.time_entries
                      if entry.description == new_description][0]
        self.assertEqual(project_id, time_entry.project_id)
        self.assertFalse(time_entry.synced)
        for tag in tags:
            self.assertTrue(tag in time_entry.tags)

    def test_update_time_entry_tags(self):
        toggl = TogglTrack(-1, -1, False)
        project_id = 3
        description = "Test time entry"
        tags = [
            "one",
            "two"
        ]
        time_entry = toggl.create_time_entry(project_id,description,tags)
        self.assertTrue(
            description in
            [entry.description for entry in toggl.time_entries]
        )
        new_tags = [
            "new tag one",
            "new tag two"
        ]
        toggl.update_time_entry(time_entry, tags=new_tags)
        self.assertTrue(
            description in
            [entry.description for entry in toggl.time_entries]
        )

        time_entry = [entry for entry in toggl.time_entries
                      if entry.description == description][0]
        self.assertEqual(project_id, time_entry.project_id)
        self.assertFalse(time_entry.synced)
        for tag in new_tags:
            self.assertTrue(tag in time_entry.tags)

    def test_time_entry_sync(self):
        wid = settings.TOGGL_WORKSPACE_ID
        togglId = settings.TOGGL_ID
        toggl = TogglTrack(wid, togglId, time_delta=timedelta(days=1))
        togglTwo = TogglTrack(wid, togglId, time_delta=timedelta(days=1))
        toggl.sync()
        for time_entry in toggl.time_entries:
            toggl.delete_time_entry(time_entry)
        project = toggl.createProject("time_entry_project_1")
        time.sleep(1)
        toggl.sync()
        togglTwo.sync()
        original_project = [project for project in toggl.projects if project.name == project.name][0]
        original_description = "test entry"
        original_tags = ["test one", "test two"]
        # LOCAL_TIMEZONE = dt.datetime.now(dt.timezone(dt.timedelta(0))).astimezone().tzinfo
        start_time = datetime.now()
        start_time = pytz.utc.localize(start_time)
        time_entry = toggl.create_time_entry(description=original_description,
                                             project_id=original_project.id,
                                             tag_names=original_tags,
                                             start_time=start_time)
        toggl.sync()
        time.sleep(1)
        togglTwo.sync()
        
        self.assertTrue(
            original_description in
            [remote_time_entry.description for remote_time_entry in togglTwo.time_entries]
        )
        entry = [remote_time_entry for remote_time_entry in togglTwo.time_entries
                 if remote_time_entry.description == original_description][0]
        self.assertEqual(
            entry.project_id,
            original_project.id
        )
        self.assertTrue(
            start_time - entry.start < timedelta(seconds=1)
        )
        for tag in original_tags:
            self.assertTrue(
                tag in entry.tags
            )

        new_project = toggl.createProject("time_entry_project_2")
        toggl.sync()
        new_project = [project for project in toggl.projects if project.name == new_project.name][0]
        new_description = "test entry two"
        new_tags = ["new tag 1", "new tag 2"]
        new_start_time = datetime.now() - timedelta(hours=1)
        new_stop_time = datetime.now()
        new_start_time = pytz.utc.localize(new_start_time)
        new_stop_time = pytz.utc.localize(new_stop_time)

        toggl.update_time_entry(entry, description=new_description,tags=new_tags,
                                start_time=new_start_time, stop_time=new_stop_time,
                                project_id=new_project.id)
        toggl.sync()
        togglTwo.sync()

        self.assertTrue(
            new_description in
            [remote_time_entry.description for remote_time_entry in togglTwo.time_entries]
        )
        entry = [remote_time_entry for remote_time_entry in togglTwo.time_entries
                 if remote_time_entry.description == new_description][0]

        self.assertEqual(
            entry.project_id,
            new_project.id
        )
        self.assertTrue(
            new_start_time - entry.start < timedelta(seconds=1)
        )
        for tag in new_tags:
            self.assertTrue(
                tag in entry.tags
            )
        toggl.delete_time_entry(entry)
        toggl.sync()
        togglTwo.sync()
        self.assertFalse(
            new_description in
            [remote_time_entry.description for remote_time_entry in togglTwo.time_entries]
        )

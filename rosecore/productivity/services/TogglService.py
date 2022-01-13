from django.conf import settings
import random
from typing import List
from productivity.libs.Toggl.TogglTrack import TogglTrack
from productivity.libs.Toggl.Project import Project


class TogglService:
    _toggl = TogglTrack(settings.TOGGL_WORKSPACE_ID,
                        settings.TOGGL_ID)

    @staticmethod
    def sync() -> None:
        """
        syncs the toggle databse
        """
        if not settings.TESTING:
            TogglService._toggl.sync()
    
    @staticmethod
    def getProject(id: str) -> dict:
        """
        gets a project(may not my synced
        """
        project = [project for project in TogglService._toggl.projects if str(project.id) == str(id)][0]
        return TogglService._formatExport(project)

    @staticmethod
    def getAllProjects() -> List[dict]:
        """
        Gets all projects
        """
        return [TogglService._formatExport(project) for project in TogglService._toggl.projects]

    @staticmethod
    def createProject(name: str) -> str:
        """
        Creates a project and returns the toggl id,
        if settings.TESTING then id is a faked id, not valid in toggl
        """
        project = TogglService._toggl.createProject(name)
        if settings.TESTING:
            TogglService._toggl.fake_project_id(project, random.randint(0, 10000000000))
        project = [project for project in TogglService._toggl.projects if project.name == name][0]
        return str(project.id)

    @staticmethod
    def updateProject(data: dict) -> None:
        """
        Updates a project, just name for now
        """
        project = [project for project in TogglService._toggl.projects if str(data["id"]) == str(project.id)][0]
        TogglService._toggl.updateProject(project, data["name"])
        TogglService.sync()

    @staticmethod
    def deleteProject(project_id: str) -> None:
        """
        deletes a project with a specified id
        """
        project = [project for project in TogglService._toggl.projects if str(project_id) == str(project.id)][0]
        TogglService._toggl.deleteProject(project)
        TogglService.sync()

    @staticmethod
    def getProjectWithNameOrCreate(name: str) -> str:
        """
        gets a project with a specific name or creates the project
        returns the id
        """
        for project in TogglService.getAllProjects():
            if project["name"] == name:
                return project["id"]
        return TogglService.createProject(name)

    @staticmethod
    def _formatExport(project: Project) -> dict:
        """
        A simple formatter that formats the project for export to the rest of the application
        """
        return {
            "id": str(project.id),
            "name": project.name,
            "archived": not project.active
        }

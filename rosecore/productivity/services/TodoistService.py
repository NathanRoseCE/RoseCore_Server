from django.conf import settings
from todoist import TodoistAPI
from typing import Iterable


class TodoistService:
    _todoist = TodoistAPI(settings.TODOIST_KEY)

    @staticmethod
    def createProject(name: str, parent_id: str = None) -> str:
        if parent_id is None:
            project = TodoistService._todoist.projects.add(name)
        else:
            project = TodoistService._todoist.projects.add(name, parent_id=int(parent_id))
        TodoistService._todoist.commit()
        return TodoistService._formatExport(project)["id"]

    @staticmethod
    def deleteProject(id: str) -> None:
        project = TodoistService._todoist.projects.get_by_id(int(id))
        project.delete()
        TodoistService._todoist.commit()

    @staticmethod
    def getProject(id: str) -> dict:
        TodoistService.sync()
        project = TodoistService._todoist.projects.get_by_id(int(id))
        return TodoistService._formatExport(project)

    @staticmethod
    def updateProject(data: dict) -> None:
        project = TodoistService._todoist.projects.get_by_id(int(data["id"]))
        if data["parent_id"] is not None:
            project.move(parent_id=int(data["parent_id"]))
        project.update(name=data["name"])
        TodoistService._todoist.commit()

    @staticmethod
    def getAllProjects()->Iterable[dict]:
        TodoistService.sync()
        return [
            TodoistService._formatExport(project) for project in TodoistService._todoist.state["projects"]
        ]

    @staticmethod
    def sync()->None:
        TodoistService._todoist.sync()

    @staticmethod
    def _formatExport(project) -> dict:
        return {
            "id": str(project.data["id"]) if project.data["id"] is not None else None,
            "name": str(project.data["name"]),
            "parent_id": str(project.data["parent_id"]) if project.data["parent_id"] is not None else None,
            "archived": project.data["is_archived"] == 1,
        }

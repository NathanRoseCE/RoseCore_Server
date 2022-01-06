from django.conf import settings
from todoist import TodoistAPI
from typing import Iterable

import datetime


class TodoistService:
    _todoist = TodoistAPI(settings.TODOIST_KEY)

    @staticmethod
    def sync()->None:
        if not settings.TESTING:
            TodoistService._todoist.sync()

    @staticmethod
    def createProject(name: str, parent_id: str = None) -> str:
        if parent_id is None:
            project = TodoistService._todoist.projects.add(name)
        else:
            project = TodoistService._todoist.projects.add(name, parent_id=int(parent_id))
        TodoistService._todoist.commit()
        return TodoistService._formatProjectExport(project)["id"]

    @staticmethod
    def deleteProject(id: str) -> None:
        project = TodoistService._todoist.projects.get_by_id(int(id))
        project.delete()
        TodoistService._todoist.commit()

    @staticmethod
    def getProject(id: str) -> dict:
        TodoistService.sync()
        project = TodoistService._todoist.projects.get_by_id(int(id))
        return TodoistService._formatProjectExport(project)

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
            TodoistService._formatProjectExport(project) for project in TodoistService._todoist.state["projects"]
        ]

    @staticmethod
    def createTask(content:str,
                   description:str="",
                   project_id:str="",
                   priority:int=3,
                   due_string: str="",
                   **args) -> str:
        """
        Creates a task and returns the new id
        """
        task = TodoistService._todoist.add_item(content=content,
                                                description=description,
                                                project_id=int(project_id),
                                                priority=priority,
                                                due_string=due_string,
                                                **args)

        TodoistService._todoist.commit()
        return TodoistService._formatTaskExport(task)["id"]

    @staticmethod
    def deleteProject(id: str) -> None:
        raise NotImplemented

    @staticmethod
    def getProject(id: str) -> dict:
        raise NotImplemented

    @staticmethod
    def updateProject(data: dict) -> None:
        raise NotImplemented
    
    @staticmethod
    def _formatProjectExport(project) -> dict:
        return {
            "id": str(project.data["id"]) if project.data["id"] is not None else None,
            "name": str(project.data["name"]),
            "parent_id": str(project.data["parent_id"]) if project.data["parent_id"] is not None else None,
            "archived": project.data["is_archived"] == 1,
        }

    @staticmethod
    def _formatTaskExport(task) -> dict:
        return {
            "id": str(task.data["id"]) if task.data["id"] is not None else None,
            "content": str(task.data["content"]),
            "description": str(task.data["description"]),
            "project_id": str(task.data["project_id"]) if task.data["project_id"] is not None else None,
            "priority": int(task.data["priority"]),
            "due_string": int(task.data["due_string"]),
            "completed": task.data["checked"] == 1,
        }

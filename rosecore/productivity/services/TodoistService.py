from django.conf import settings
from todoist import TodoistAPI
from typing import Iterable
from copy import copy

import datetime


class TodoistService:
    _todoist = TodoistAPI(settings.TODOIST_KEY)

    @staticmethod
    def sync()->None:
        """
        Syncs to remote if not testing
        """
        if not settings.TESTING:
            TodoistService._todoist.sync()

    @staticmethod
    def createProject(name: str, parent_id: str = None) -> str:
        """
        Creates a new project
        """
        if parent_id is None:
            project = TodoistService._todoist.projects.add(name)
        else:
            project = TodoistService._todoist.projects.add(name, parent_id=int(parent_id))
        TodoistService._todoist.commit()
        return TodoistService._formatProjectExport(project)["id"]

    @staticmethod
    def deleteProject(id: str) -> None:
        """
        Deletes a project
        """
        project = TodoistService._todoist.projects.get_by_id(int(id))
        project.delete()
        TodoistService._todoist.commit()

    @staticmethod
    def getProject(id: str) -> dict:
        """
        Gets a project in an id
        """
        TodoistService.sync()
        project = TodoistService._todoist.projects.get_by_id(int(id))
        return TodoistService._formatProjectExport(project)

    @staticmethod
    def updateProject(data: dict) -> None:
        """
        Updates project
        """
        project = TodoistService._todoist.projects.get_by_id(int(data["id"]))
        if data["parent_id"] is not None:
            project.move(parent_id=int(data["parent_id"]))
        project.update(name=data["name"])
        TodoistService._todoist.commit()

    @staticmethod
    def getAllProjects()->Iterable[dict]:
        """
        Gets all project detail
        """
        TodoistService.sync()
        return [
            TodoistService._formatProjectExport(project) for project in TodoistService._todoist.state["projects"]
        ]

    @staticmethod
    def getProjectWithNameOrCreate(name: str)->str:
        """
        gets a project with a specific name or creates the project
        returns the id of the project as a string
        """
        for project in TodoistService.getAllProjects():
            if project["name"] == name:
                return project["id"]
        return TodoistService.createProject(name)

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
    def deleteTask(id: str) -> None:
        """
        deletes a task from Todosit
        """
        task = TodoistService._todoist.items.get_by_id(int(id))
        task.delete()
        TodoistService.sync()

    @staticmethod
    def getTask(id: str) -> dict:
        """
        gets a task
        """
        TodoistService.sync()
        task = TodoistService._todoist.items.get_by_id(int(id))
        return TodoistService._formatTaskExport(task)

    @staticmethod
    def updateTask(data: dict) -> None:
        """
        Updates a task for a given id, data is handed to todoist.sync api
        """
        data = copy(data)
        task = TodoistService._todoist.items.get_by_id(int(data["id"]))
        del data["id"]
        task.update(data)
        TodoistService.sync()
        raise NotImplemented

    @staticmethod
    def completeTask(id: str) -> None:
        """
        Marks a task as completed
        """
        task = TodoistService._todoist.items.get_by_id(int(id))
        task.complete()
        TodoistService.sync()
    
    @staticmethod
    def _formatProjectExport(project) -> dict:
        """
        Formats the project export
        """
        return {
            "id": str(project.data["id"]) if project.data["id"] is not None else None,
            "name": str(project.data["name"]),
            "parent_id": str(project.data["parent_id"]) if project.data["parent_id"] is not None else None,
            "archived": project.data["is_archived"] == 1,
        }

    @staticmethod
    def _formatTaskExport(task) -> dict:
        """
        Formats the task export 
        """
        return {
            "id": str(task.data["id"]) if task.data["id"] is not None else None,
            "content": str(task.data["content"]),
            "description": str(task.data["description"]),
            "project_id": str(task.data["project_id"]) if task.data["project_id"] is not None else None,
            "priority": int(task.data["priority"]),
            "due_string": int(task.data["due_string"]),
            "completed": task.data["checked"] == 1,
        }

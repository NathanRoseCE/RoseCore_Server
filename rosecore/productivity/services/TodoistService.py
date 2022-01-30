from django.conf import settings
from django.db.models.query_utils import DeferredAttribute
from todoist import TodoistAPI
from typing import Iterable
from copy import copy
import json

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
    def commit() -> None:
        """
        commits
        """
        if not settings.TESTING:
            TodoistService._todoist.commit()

    @staticmethod
    def createProject(name: str, parent_id: str = None) -> str:
        """
        Creates a new project
        """
        if parent_id is None:
            project = TodoistService._todoist.projects.add(name)
        else:
            pid = parent_id
            project = TodoistService._todoist.projects.add(name, parent_id=pid)
        TodoistService.commit()
        return TodoistService._formatProjectExport(project)["id"]

    @staticmethod
    def deleteProject(id: str) -> None:
        """
        Deletes a project
        """
        project = TodoistService._todoist.projects.get_by_id(TodoistService.format_id(id))
        project.delete()
        f_id = TodoistService.format_id(id)
        if isinstance(f_id, str):
            match_project = [project for project in TodoistService._todoist.state["projects"]
                             if project.temp_id == id][0]
            TodoistService._todoist.state["projects"].remove(match_project)
        TodoistService.commit()

    @staticmethod
    def getProject(id: str) -> dict:
        """
        Gets a project in an id
        """
        TodoistService.sync()
        project = TodoistService._todoist.projects.get_by_id(TodoistService.format_id(id))
        return TodoistService._formatProjectExport(project)

    @staticmethod
    def updateProject(data: dict) -> None:
        """
        Updates project
        """
        project = TodoistService._todoist.projects.get_by_id(TodoistService.format_id(data["id"]))
        if "parent_id" in data:
            if data["parent_id"] is not None:
                project.move(parent_id=TodoistService.format_id(data["parent_id"]))
        project.update(name=data["name"])
        TodoistService.commit()

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
    def getAllTasks()->Iterable[dict]:
        """
        Gets all of the tasks
        """
        TodoistService.sync()
        return [
            TodoistService._formatTaskExport(task) for task in TodoistService._todoist.items.all()
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
        # print()
        # print(f"project id: {TodoistService.format_id(project_id)}")
        # print(f'known projects: {[project["id"] for project in TodoistService.getAllProjects()]}')
        # print(f'matches: {[(TodoistService.format_id(project_id) ==project["id"]) for project in TodoistService.getAllProjects()]}')
        task = TodoistService._todoist.add_item(content=content,
                                                description=description,
                                                project_id=TodoistService.format_id(project_id),
                                                priority=priority,
                                                due_string=due_string,
                                                **args)
        if "error" in task:
            print(f"content: {content}")
            print(f"description: {description}")
            print(f"project_id: {project_id}")
            print(json.dumps(task, indent=2))
            raise ValueError(task)
        TodoistService.commit()
        return TodoistService._formatTaskExport(task)["id"]

    @staticmethod
    def deleteTask(id: str) -> None:
        """
        deletes a task from Todosit
        """
        task = TodoistService._todoist.items.get_by_id(TodoistService.format_id(id))
        task.delete()
        TodoistService.commit()

    @staticmethod
    def getTask(id: str) -> dict:
        """
        gets a task
        """
        TodoistService.sync()
        task = TodoistService._todoist.items.get_by_id(TodoistService.format_id(id))
        return TodoistService._formatTaskExport(task)

    @staticmethod
    def updateTask(data: dict) -> None:
        """
        Updates a task for a given id, data is handed to todoist.sync api
        """
        data = copy(data)
        task = TodoistService._todoist.items.get_by_id(TodoistService.format_id(data["id"]))
        if "id" in data:
            del data["id"]
        task.update(data)
        TodoistService.sync()

    @staticmethod
    def completeTask(id: str) -> None:
        """
        Marks a task as completed
        """
        task = TodoistService._todoist.items.get_by_id(TodoistService.format_id(id))
        task.close()
        TodoistService.sync()
    
    @staticmethod
    def _formatProjectExport(project) -> dict:
        """
        Formats the project export
        """
        project_export = {
            "id": str(project.data["id"]) if project.data["id"] is not None else None,
            "name": str(project.data["name"]),
        }
        if "parent_id" in project.data:
            project_export["parent_id"] = str(project.data["parent_id"]) if project.data["parent_id"] is not None else None
        if "archived" in project.data:
            project_export["archived"] = project.data["is_archived"] == 1
        return project_export

    @staticmethod
    def _formatTaskExport(task) -> dict:
        """
        Formats the task export 
        """
        return {
            "id": str(task["id"]) if task["id"] is not None else None,
            "content": str(task["content"]),
            "description": str(task["description"]),
            "project_id": str(task["project_id"]) if task["project_id"] is not None else None,
            "priority": TodoistService.format_id(task["priority"]),
            "due_string": TodoistService.format_id(task["due"]["string"]) if task["due"] is not None else None,
            "completed": task["checked"] == 1,
        }

    @staticmethod
    def format_id(id: str):
        if isinstance(id, int):
            return id
        elif isinstance(id, str):
            try:
                return_id = int(id)
            except ValueError:
                return_id = id
            return return_id
        elif isinstance(id, DeferredAttribute):
            print(dir(id))
            print(f"tmpid: {dir(tmp_id['field'])}")
            print(f"tmpid2: {id.first()}")
            return TodoistService.format_id(id.data["id"])

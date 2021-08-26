from .models import Project
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .exceptions import InvalidProject, APIThrottled
from django.conf import settings
from todoist import TodoistAPI
from typing import Iterable
import requests
import json
from requests.auth import HTTPBasicAuth


class ProjectService:
    @staticmethod
    def get_projects(limit=None, **filters):
        return Project.objects.all()[:limit]

    @staticmethod
    def get_project_or_404(project_id):
        return get_object_or_404(Project, pk=project_id)

    @staticmethod
    def createProject(name:str, commit=True, **args)->Project:
        todoistId = args["todoistId"] if "todoistId" in args else ""
        togglId = args["togglId"] if "togglId" in args else ""
        parent=args["parent"] if "parent" in args else None
        if todoistId:
            ProjectService.validateTodoistId(todoistId)
        else:
            todoistId = TodoistService.createProject(name,
                                                     parent_id=parent.todoistId if parent is not None else None)

        if togglId:
            ProjectService.validateTogglId(togglId)
        else:
            togglId = TogglService.createProject(name)
        project = Project(
            name=name,
            todoistId=todoistId,
            togglId=togglId,
            parent=parent
        )
        if commit:
            project.save()
        return project

    @staticmethod
    def updateProject(project: Project)->Project:
        TodoistService.updateProject({"id": project.todoistId, "name": project.name, "parent_id": project.parent.todoistId if project.parent is not None else None})
        TogglService.updateProject({"id": project.togglId, "name": project.name})
        project.save()

    @staticmethod
    def deleteProject(project: Project)->Project:
        TodoistService.deleteProject(project.todoistId)
        TogglService.deleteProject(project.togglId)
        project.delete()
    
    @staticmethod
    def validateTodoistId(todoistId: str):
        if not (todoistId in [project["id"] for project in TodoistService.getAllProjects()]):
            raise InvalidProject(
                "todoistId", str(todoistId)
            )

    @staticmethod
    def validateTogglId(togglId: str):
        if not (togglId in [project["id"] for project in TogglService.getAllProjects()]):
            raise InvalidProject(
                "togglId", str(togglId)
            )

    @staticmethod
    def sync():
        TodoistService.sync()
        todoistProjects = TodoistService.getAllProjects()
        togglProjects = TogglService.getAllProjects()
        unsynced = ProjectService._nonIdMatch(todoistProjects, togglProjects)
        ProjectService._handleUnsynced(unsynced)

    @staticmethod
    def _nonIdMatch(todoistProjects: dict, togglProjects: dict) -> dict:
        todoistCreate = []
        todoistUpdate = []
        togglCreate = []
        togglUpdate = []

        for project in Project.objects.all():
            try:
                match = [todoistProject for todoistProject in todoistProjects
                         if todoistProject["id"] == project.todoistId][0]
                todoistProjects.remove(match)
                if match["name"] != project.name:
                    match["name"] = project.name
                    todoistUpdate.append(match)
            except IndexError:
                todoistCreate.append(project)
            try:
                match = [togglProject for togglProject in togglProjects
                         if togglProject["id"] == project.togglId][0]
                togglProjects.remove(match)
                if match["name"] != project.name:
                    match["name"] = project.name
                    togglUpdate.append(match)
            except IndexError:
                togglCreate.append(project)
        return {
            "todoist": {
                "create": todoistCreate,
                "update": todoistUpdate,
                "delete": todoistProjects
            },
            "toggl": {
                "create": togglCreate,
                "update": togglUpdate,
                "delete": togglProjects
            }
        }

    @staticmethod
    def _handleUnsynced(unsynced: dict) -> None:
        [TodoistService.deleteProject(project["id"])
         for project in unsynced["todoist"]["delete"]]
        [TodoistService.update(project)
         for project in unsynced["todoist"]["update"]]
        for project in unsynced["todoist"]["create"]:
            project.todoistId = TodoistService.createProject(project.name)
            project.save()

        [TogglService.deleteProject(project["id"])
         for project in unsynced["toggl"]["delete"]]
        [TogglService.update(project)
         for project in unsynced["toggl"]["update"]]
        for project in unsynced["toggl"]["create"]:
            project.togglId = TogglService.createProject(project.name)
            project.save()


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


class TogglService:
    _id = settings.TOGGL_ID
    _workspace_id = settings.TOGGL_WORKSPACE_ID

    @staticmethod
    def getProject(id: str) -> dict:
        response = requests.get(
            "https://api.track.toggl.com/api/v8/projects/" + str(id),
            auth=HTTPBasicAuth(TogglService._id, "api_token")
        )
        return TogglService._formatExport(TogglService._parseJsonResponse(response)["data"])

    @staticmethod
    def getAllProjects() -> dict:
        response = requests.get(
            "https://api.track.toggl.com/api/v8/workspaces/" + str(TogglService._workspace_id) + "/projects",
            auth=HTTPBasicAuth(TogglService._id, "api_token"),
        )
        projects = TogglService._parseJsonResponse(response)
        if projects is None:
            return []
        return [TogglService._formatExport(project) for project in projects]

    @staticmethod
    def createProject(name: str) -> id:
        response = requests.post(
            "https://api.track.toggl.com/api/v8/projects",
            auth=HTTPBasicAuth(TogglService._id, "api_token"),
            data=json.dumps({"project": {
                "name": name,
                "wid": TogglService._workspace_id
            }}),
            headers={
                "Content-Type": "application/json"
            }
        )
        return TogglService._formatExport(TogglService._parseJsonResponse(response)["data"])["id"]

    @staticmethod
    def updateProject(data: dict) -> None:
        response = requests.put(
            "https://api.track.toggl.com/api/v8/projects/" + str(data["id"]),
            auth=HTTPBasicAuth(TogglService._id, "api_token"),
            data=json.dumps({"project": {
                "name": data["name"],
                "wid": TogglService._workspace_id
            }}),
            headers={
                "Content-Type": "application/json"
            }
        )
        TogglService._formatExport(TogglService._parseJsonResponse(response)["data"])

    @staticmethod
    def deleteProject(id: str) -> id:
        response = requests.delete(
            "https://api.track.toggl.com/api/v8/projects/" + str(id),
            auth=HTTPBasicAuth(TogglService._id, "api_token"),
            headers={
                "Content-Type": "application/json"
            }
        )
        TogglService._parseJsonResponse(response)

    @staticmethod
    def _formatExport(project) -> dict:
        return {
            "id": str(project["id"]),
            "name": project["name"],
            "archived": not project["active"]
        }

    @staticmethod
    def _parseJsonResponse(response):
        if str(response) != "<Response [200]>":
            if str(response) == "<Response [429]>":
                raise APIThrottled
            raise Exception(response.text)
        return json.loads(response.text)

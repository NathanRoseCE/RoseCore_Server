from .models import Project
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .exceptions import InvalidProject
from django.conf import settings
from todoist import TodoistAPI
from typing import Iterable


class ProjectService:
    @staticmethod
    def get_projects(limit=None, **filters):
        return Project.objects.all()[:limit]

    @staticmethod
    def get_project_or_404(project_id):
        return get_object_or_404(Project, pk=project_id)

    @staticmethod
    def createProject(name:str, **args)->Project:
        todoistId = args["todoistId"] if "todoistId" in args else ""
        togglId = args["togglId"] if "togglId" in args else ""
        if todoistId:
            ProjectService.validateTodoistId(todoistId)
        else:
            todoistId = TodoistService.createProject(name)
        if togglId:
            ProjectService.validateTodoistId(todoistId)
        else:
            pass  # Create new project in Toggl
        project = Project(
            name=name,
            todoistId=todoistId,
            togglId=togglId
        )
        project.save()
        return project

    @staticmethod
    def validateTodoistId(todoistId: str):
        raise InvalidProject(
            "todoist", str(todoistId)
        )

    @staticmethod
    def validateTogglId(togglId: str):
        raise InvalidProject(
            "toggl", str(togglId)
        )


class TodoistService:
    _todoist = TodoistAPI(settings.TODOIST_KEY)

    @staticmethod
    def createProject(name: str, parent_id: str = None) -> str:
        if parent_id is not None:
            raise NotImplementedError()
        project = TodoistService._todoist.projects.add(name)
        TodoistService._todoist.commit()
        return TodoistService._formatExport(project)["id"]

    @staticmethod
    def deleteProject(id: str) -> None:
        project = TodoistService._todoist.projects.get_by_id(int(id))
        project.delete()
        TodoistService._todoist.commit()

    @staticmethod
    def getProject(id: str) -> dict:
        project = TodoistService._todoist.projects.get_by_id(int(id))
        return TodoistService._formatExport(project)

    @staticmethod
    def getAllProjects()->Iterable[dict]:
        return [
            TodoistService._formatExport(project) for project in TodoistService._todoist.state["projects"]
        ]

    @staticmethod
    def sync()->None:
        TodoistService._todoist.sync()

    @staticmethod
    def _formatExport(project) ->dict:
        return {
            "id": str(project.data["id"]) if project.data["id"] is not None else None,
            "name": str(project.data["name"]),
            "parent_id": str(project.data["parent_id"]) if project.data["parent_id"] is not None else None,
            "archived": project.data["is_archived"] == 1,
        }

from productivity.models.Project import Project
from django.shortcuts import get_object_or_404
from .TodoistService import TodoistService
from .TogglService import TogglService
from productivity.utilities.exceptions import InvalidProject


class ProjectService:
    @staticmethod
    def get_projects(limit=None, **filters):
        return Project.objects.all()[:limit]

    @staticmethod
    def get_project_or_404(project_id):
        return get_object_or_404(Project, pk=project_id)

    @staticmethod
    def createProject(name: str, commit=True, **args) -> Project:
        todoistId = args["todoistId"] if "todoistId" in args else ""
        togglId = args["togglId"] if "togglId" in args else ""
        parent = args["parent"] if "parent" in args else None
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
    def get_root_projects(limit=None):
        return Project.objects.all().filter(parent=None)

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
        projects = Project.objects.all()
        unsynced = ProjectService._nonIdMatch(projects, todoistProjects, togglProjects)
        unsynced = ProjectService._parseForNameMatches(projects, unsynced)
        [project.save() for project in projects]
        ProjectService._handleUnsynced(unsynced)

    @staticmethod
    def _parseForNameMatches(projects, idResults: dict):
        for project in projects:
            try:
                nameMatch = [tProject for tProject in idResults["todoist"]["delete"]
                             if tProject["name"] == project.name][0]
                idResults["todoist"]["update"].append(nameMatch)
                idResults["todoist"]["delete"].remove(nameMatch)
                project.todoistId=nameMatch["id"]
            except IndexError:
                pass
            try:
                nameMatch = [tProject for tProject in idResults["toggl"]["delete"]
                             if tProject["name"] == project.name][0]
                idResults["toggl"]["update"].append(nameMatch)
                idResults["toggl"]["delete"].remove(nameMatch)
                project.togglId=nameMatch["id"]
            except IndexError:
                pass
        return idResults

    @staticmethod
    def _nonIdMatch(projects, todoistProjects: dict, togglProjects: dict) -> dict:
        todoistCreate = []
        todoistUpdate = []
        togglCreate = []
        togglUpdate = []

        for project in projects:
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

from productivity.models.Project import Project
from django.shortcuts import get_object_or_404
from .TodoistService import TodoistService
from .TogglService import TogglService
from productivity.utilities.exceptions import InvalidProject


class ProjectService:
    @staticmethod
    def get_projects(limit=None, **filters):
        """
        Gets a large project
        """
        return Project.objects.all()[:limit]

    @staticmethod
    def get_project_or_404(project_id):
        """
        Gets a project or throws a 404 exception
        """
        return get_object_or_404(Project, pk=project_id)

    @staticmethod
    def createProject(name: str, commit: bool=True, **args) -> Project:
        """
        Creates a project if the todoistId and/or togglId are present
        then it will store them else it will create new projects with 
        the name
        """
        project_args = {
            "name": name
        }
        allowedToCreate=True
        if "unsyncedSource" in args:
            project_args["unsyncedSource"] = args["unsyncedSource"]
            allowedToCreate=False
            
            
        parent = args["parent"] if "parent" in args else None
        if "todoistId" in args:
            ProjectService.validateTodoistId(args["todoistId"])
            project_args["todoistId"] = args["todoistId"]
        else:
            if allowedToCreate:
                todoistId = TodoistService.createProject(name,
                                                         parent_id=parent.todoistId if parent is not None else None)
                project_args["todoistId"] = todoistId
        if "togglId" in args:
            ProjectService.validateTogglId(args["togglId"])
            project_args["togglId"] = args["togglId"]
        else:
            if allowedToCreate:
                togglId = TogglService.createProject(name)
                project_args["togglId"] = togglId
        project = Project(
            **project_args
        )
        if commit:
            project.save()
        return project

    @staticmethod
    def get_root_projects(limit=None):
        """
        Gets all projects without parents
        """
        return Project.objects.all().filter(parent=None)[:limit]

    @staticmethod
    def updateProject(project: Project)->None:
        """
        Updates a project
        """
        TodoistService.updateProject({"id": project.todoistId, "name": project.name, "parent_id": project.parent.todoistId if project.parent is not None else None})
        TogglService.updateProject({"id": project.togglId, "name": project.name})
        project.save()

    @staticmethod
    def deleteProject(project: Project)->None:
        """
        Delets a project
        """
        TodoistService.deleteProject(project.todoistId)
        TogglService.deleteProject(project.togglId)
        project.delete()

    @staticmethod
    def markUnsynced(data: dict)->None:
        """
        Marks a project as unsyced
        """
        project = Project(**data)
        project.unsynced=True
        project.save()
        
    @staticmethod
    def validateTodoistId(todoistId: str):
        """
        ensure the todoist project id is valud
        """
        if not (todoistId in [project["id"] for project in TodoistService.getAllProjects()]):
            raise InvalidProject(
                "todoistId", str(todoistId)
            )

    @staticmethod
    def validateTogglId(togglId: str):
        """
        Ensures the toggl project id is valid
        """
        if not (togglId in [project["id"] for project in TogglService.getAllProjects()]):
            raise InvalidProject(
                "togglId", str(togglId)
            )

    @staticmethod
    def sync():
        """
        syncs all of the projects
        """
        TodoistService.sync()
        TogglService.sync()
        ProjectService._ensure_client_projects_present()
        ProjectService._check_for_unsynced_projects()

    @staticmethod
    def _ensure_client_projects_present(save: bool=True):
        """
        For all projects in the databse that are synced, ensure that
        the clients(Todoist and Toggl) have projects with the id listed
        will check for id match, then name match, then create it
        """
        for project in Project.objects.all():
            todoist_id = ProjectService._ensure_project_present_todoist(project)
            toggl_id = ProjectService._ensure_project_present_toggl(project)
            project.todoistId = todoist_id
            project.togglId = toggl_id
            if save:
                project.save()
    @staticmethod
    def _ensure_project_present_todoist(project: Project) -> str:
        """
        ensures a specified client project is present in todoist
        """
        correctProject = None
        for todoist_project in TodoistService.getAllProjects():
            if todoist_project["id"] == project.todoistId:
                correctProject = todoist_project
                break
            elif todoist_project["name"] == project.name:
                correctProject = todoist_project
        if correctProject is not None:
            return correctProject["id"]
        else:
            project_args = {
                "name": project.name
            }
            if project.parent is not None:
                project_args["parent_id"] = project.parent.todoistId
            todoist_id = TodoistService.createProject(**project_args)
            return todoist_id


    @staticmethod
    def _ensure_project_present_toggl(project: Project) -> str:
        """
        ensure a given client project is present todoist
        """
        correctProject = None
        for toggl_project in TogglService.getAllProjects():
            if toggl_project["id"] == project.todoistId:
                correctProject = toggl_project
                break
            elif toggl_project["name"] == project.name:
                correctProject = toggl_project
        if correctProject is not None:
            return correctProject["id"]
        else:
            project_args = {
                "name": project.name
            }
            toggl_id = TogglService.createProject(**project_args)
            return toggl_id

    @staticmethod
    def _check_for_unsynced_projects() -> None:
        """
        ensures that all projects that exist only on todoist/toggl are
        present and mark as unsynced with the correct source
        """
        ProjectService._check_for_unsynced_todoist_projects()

    @staticmethod
    def _check_for_unsynced_todoist_projects() -> None:
        for todoist_project in TodoistService.getAllProjects():
            if not todoist_project["id"] in [project.todoistId for project in ProjectService.get_projects()]:
                ProjectService.createProject(todoist_project["name"],
                                             todoistId=todoist_project["id"],
                                             unsyncedSource="todoist")

import requests
from typing import Dict, Any, List

from requests.auth import HTTPBasicAuth
from .Exceptions import APIThrottled
from .Project import Project
from copy import copy
import json

class TogglTrack:
    """
    The main API class for toggl track for rosecore, the changes are local until sync() is called
    """
    
    def __init__(self, workspace_id: int, api_token: int, allowSync:bool=True):
        """
        initializes the API
         - workspace_id: id of workspace
         - api_token: id token for toggl api
         - allowSync: passes sync messages to toggl
        """
        self._workspace_id = workspace_id
        self._api_token = api_token
        self._allowSync = allowSync
        self._projects = {}
        self._new_projects=[]
        self._main_url = "https://api.track.toggl.com/api/v8"
        self._project_url = self._main_url + "/projects"
        self._workspace_url = self._main_url + "/workspaces/" + str(self._workspace_id)

    @property
    def projects(self) -> List[Project]:
        """
        Gets projects that are not to be deleted, and included ones to be created
        """
        projects = copy(self._new_projects)
        projects.extend([project for id, project in self._projects.items() if not project.to_delete])
        return projects

    def createProject(self, name: str) -> Project:
        """
        Creates a toggl project with a gieven name
        """
        newProject = Project()
        newProject.name = name
        newProject.workspace_id = self._workspace_id
        self._new_projects.append(newProject)
        return newProject
        

    def updateProject(self, project: Project, newName: str) -> None:
        """
        Updates a projects name
        """
        if project.id in self._projects:
            self._projects[project.id].name = newName
            self._projects[project.id].synced = False
        elif project.id in [m_project.id for m_project in self._new_projects]:
            index = [m_project.id for m_project in self._new_projects].index(project.id)
            project = self._new_projects[index]
            project.name = newName
            project.synced = False
        else:
            raise ValueError(f"Project:{project.name} is not a known project")

    def deleteProject(self, project: Project) -> None:
        """
        Deletes a project
        """
        if project.id in self._projects:
            self._projects[project.id].to_delete = True
        elif project in self._new_projects:
            self._new_projects.remove(project)
        else:
            raise ValueError(f"Project:{project.name} is not a known project")

    def _getProjects(self, refresh: bool=True) -> None:
        """
        Gets all projects from external URL, does not check allowSync
        """
        if refresh:
            self._projects = {}
        response = requests.get(self._workspace_url + "/projects",
                                auth=HTTPBasicAuth(self._api_token, "api_token"))
        projects_json = self._parseResponse(response)
        if projects_json is not None:
            for project_json in projects_json:
                project = Project()
                project.fromJson(project_json)
                project.synced=True
                self._projects[project.id] = project
        
    def sync(self) -> None:
        """
        syncs up local and remote toggl instances, if allowSync is true
        """
        if self._allowSync:
            self._syncProjects()

    def _createRemoteProjects(self) -> None:
        """
        Creates the projects in remote and stores them in the _projects
        """
        for new_project_config in self._new_projects:
            response = requests.post(self._project_url,
                                     auth=HTTPBasicAuth(self._api_token, "api_token"),
                                     data=json.dumps({"project": {
                                         "name": new_project_config.name,
                                         "wid": new_project_config.workspace_id
                                     }}),
                                     headers={
                                         "Content-Type": "application/json"
                                     })
            new_project = self._parseToProject(self._parseResponse(response))
            new_project.synced=True
            self._projects[new_project.id] = new_project

    def _syncProjects(self) -> None:
        """
        sync projects, pushes unsynced then pulls
        """
        unsyncedProjects = [project for id, project in self._projects.items() if not project.synced]
        for project in unsyncedProjects:
            response = requests.put(self._project_url + "/" + str(project.id),
                                     auth=HTTPBasicAuth(self._api_token, "api_token"),
                                    data = json.dumps({"project": {
                                        "name": project.name,
                                        "wid": project.workspace_id
                                    }}),
                                    headers={
                                        "Content-Type": "application/json"
                                    })
            # I do not update the projects dict because its about to be refresshed
            self._parseResponse(response)
        deleteProjects = [project for id, project in self._projects.items() if project.to_delete]
        for project in deleteProjects:
            response = requests.delete(
                self._project_url + "/" + str(project.id),
                auth=HTTPBasicAuth(self._api_token, "api_token"),
                headers={
                    "Content-Type": "application/json"
                })
            self._parseResponse(response)
                
        for project in self._new_projects:
            response = requests.post(self._project_url,
                                     auth=HTTPBasicAuth(self._api_token, "api_token"),
                                     data=json.dumps({"project": {
                                         "name": project.name,
                                         "wid": project.workspace_id
                                     }}),
                                     headers={
                                         "Content-Type": "application/json"
                                     })
            self._parseResponse(response)
        self._new_projects.clear()
        self._getProjects(refresh=True)
        
    
    def _parseToProject(self, projectConfig: Dict[str,Any]) -> Project:
        """
        turns a json project into a project obj
        """
        project = Project()
        project.fromJson(projectConfig)
        return project
    
    def _parseResponse(self, response) -> Dict[str, Any]:
        """
        handles any errors and returns a json config
        """
        if str(response) != "<Response [200]>":
            if str(response) == "<Response [429]>":
                raise APIThrottled
            raise Exception(response.text)
        return json.loads(response.text)

    def fake_id(self, project: Project, id: int) -> None:
        """
        mocks a project that is only local with a fake ID,
        only use in testing
        NOTE: THIS WILL BE OVERRIDEN IF SYNCED!
        NOTE: THIS IS NOT A VALID ID, TESTING ONLY
        NOTE: MAY OVERRIDE EXISTING PROJECTS
        """
        if project in self._new_projects:
            project.id = id
            self._projects[id] = project
            self._new_projects.remove(project)
        else:
            raise ValueError(f"{project.name} is not a known project")

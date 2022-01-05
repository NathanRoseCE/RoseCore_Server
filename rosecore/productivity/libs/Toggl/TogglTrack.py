from datetime import datetime
import requests
from typing import Dict, Any, List

from requests.auth import HTTPBasicAuth
from .Exceptions import APIThrottled
from .Project import Project
from .TimeEntry import TimeEntry
from copy import copy
import json

from datetime import timedelta
import pytz

class TogglTrack:
    """
    The main API class for toggl track for rosecore, the changes are local until sync() is called
    """
    
    def __init__(self,
                 workspace_id: int,
                 api_token: int,
                 time_delta:timedelta=timedelta(weeks=1),
                 allowSync:bool=True):
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
        self._time_entries_url = self._main_url + "/time_entries"
        self._new_time_entries=[]
        self._time_entries={}
        self._time_delta = time_delta

    @property
    def projects(self) -> List[Project]:
        """
        Gets projects that are not to be deleted, and included ones to be created
        """
        projects = copy(self._new_projects)
        projects.extend([project for id, project in self._projects.items() if not project.to_delete])
        return projects

    @property
    def time_entries(self) -> List[TimeEntry]:
        entries = copy(self._new_time_entries)
        entries.extend([entry for id, entry in self._time_entries.items() if not entry.to_delete])
        return entries

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
        elif project.name in [m_project.name for m_project in self._new_projects]:
            index = [m_project.name for m_project in self._new_projects].index(project.name)
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
            self._sync_time_entries()

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

    def fake_project_id(self, project: Project, id: int) -> None:
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

    def create_time_entry(self,
                          project_id: int,
                          description: str,
                          tag_names: List[str],
                          start_time: datetime = datetime.now()) -> TimeEntry:
        """
        Creates a time entry in toggle
        """
        time_entry = TimeEntry()
        time_entry.description = description
        time_entry.start = start_time
        time_entry.workspace_id = self._workspace_id
        time_entry.project_id = project_id
        time_entry.tags = copy(tag_names)
        time_entry.synced = False
        self._new_time_entries.append(time_entry)
        return time_entry

    def update_time_entry(self,
                          time_entry: TimeEntry,
                          description: str = None,
                          tags: List[str] = None,
                          start_time: datetime = None,
                          stop_time: datetime = None,
                          project_id: int = None)->None:
        """
        Updates a time entry
        """
        id = time_entry.id
        if time_entry.id in self._time_entries:
            self._time_entries[id].synced = False
            if description is not None:
                self._time_entries[id].description = description
            if tags is not None:
                self._time_entries[id].tags = copy(tags)
            if start_time is not None:
                self._time_entries[id].start = start_time
            if stop_time is not None:
                self._time_entries[id].stop = stop_time
            if project_id is not None:
                self._time_entries[id].project_id = project_id
        elif time_entry.description in [entry.description for entry in self._new_time_entries]:
            index = [entry.description for entry in self._new_time_entries].index(time_entry.description)
            entry = self._new_time_entries[index]
            entry.synced = False
            if description is not None:
                entry.description = description
            if tags is not None:
                entry.tags = copy(tags)
            if start_time is not None:
                entry.start = start_time
            if stop_time is not None:
                entry.stop = stop_time
            if project_id is not None:
                entry.project_id = project_id
        else:
            raise ValueError(f"Time Entry {time_entry.id}, {time_entry.description} is not known")
        
    def delete_time_entry(self, time_entry: TimeEntry) -> None:
        """
        Deletes a time Entry
        """
        if time_entry.id in self._time_entries:
            self._time_entries[time_entry.id].to_delete = True
        elif time_entry.description in [entry.description for entry in self._new_time_entries]:
            entry = [entry for entry in self._new_time_entries
                     if entry.description == time_entry.description][0]
            self._new_time_entries.remove(entry)
        else:
            raise ValueError("Time Entry {time_entry.description} is not known")
            
    def stop_time_entry(self, time_entry: TimeEntry) -> None:
        """
        Stops a time entry
        """
        if time_entry.id in self._time_entries:
            self._time_entries[time_entry.id].stop = datetime.now()
        elif time_entry.description in [entry.description for entry in self._new_time_entries]:
            entry = [entry for entry in self._new_time_entries
                     if entry.description == time_entry.description][0]
            entry.stop = datetime.now()
        else:
            raise ValueError("Time Entry {time_entry.description} is not known")

    def _sync_time_entries(self, delta: timedelta=None) -> None:
        """
        gets all time entries within the delta, if none, uses self._time_delta
        """
        self._create_new_time_entries()
        self._update_time_entries()
        self._delete_time_entries()
        self._fetch_time_entries(delta, True)

    def _delete_time_entries(self) -> None:
        """
        Deletes all time entries that are marked to delete
        """
        for id, entry in self._time_entries.items():
            if entry.to_delete:
                response = requests.delete(self._time_entries_url + "/" + str(id),
                                           auth=HTTPBasicAuth(self._api_token, "api_token")
                                           )
                self._parseResponse(response)
        
    def _fetch_time_entries(self, delta: timedelta=None, refresh=True) -> None:
        """
        fetches the time entries within the +-time delta
        if refresh is set it will clear the time entries 
        """
        if refresh:
            self._time_entries={}
        if delta is None:
            delta = self._time_delta
        start_time = datetime.now() - delta
        stop_time = datetime.now() + delta
        start_time = pytz.utc.localize(start_time)
        stop_time = pytz.utc.localize(stop_time)
        response = requests.get(self._time_entries_url,
                                auth=HTTPBasicAuth(self._api_token, "api_token"),
                                params={
                                    "start_date": start_time.isoformat("T", "seconds"),
                                    "stop_date": stop_time.isoformat("T", "seconds"),
                                })
        entries_json = self._parseResponse(response)
        for entry_json in entries_json:
            entry = TimeEntry()
            entry.fromJson(entry_json)
            entry.id = int(entry_json["id"])
            self._time_entries[entry.id] = entry

    def _create_new_time_entries(self, clear_new=True) -> None:
        """
        Creates new time entries and then clears
        """
        for time_entry in self._new_time_entries:
            jsonData = json.dumps({
                "time_entry": time_entry.toJson()
            })
            response = requests.post(self._time_entries_url,
                                    auth=HTTPBasicAuth(self._api_token, "api_token"),
                                    data=jsonData)
            self._parseResponse(response)
        if clear_new:
            self._new_time_entries = []

    def _update_time_entries(self) -> None:
        """
        Update Time entriess time entries
        """
        for id, time_entry in self._time_entries.items():
            if time_entry.synced:
                continue
            response = requests.put(self._time_entries_url + "/" + str(id),
                                    auth=HTTPBasicAuth(self._api_token, "api_token"),
                                    data=json.dumps({
                                        "time_entry": time_entry.toJson()
                                    }))
            self._parseResponse(response)
            time_entry.synced = True
            

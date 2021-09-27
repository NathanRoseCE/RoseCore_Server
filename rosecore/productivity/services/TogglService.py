from django.conf import settings
import requests
import json
from requests.auth import HTTPBasicAuth
from productivity.utilities.exceptions import APIThrottled


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

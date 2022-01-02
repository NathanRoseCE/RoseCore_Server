from dataclasses import dataclass
from datetime import datetime
from typing import List
import json
from dateutil import parser


@dataclass
class TimeEntry:
    description : str = ""
    start: datetime = None
    stop: datetime = None
    workspace_id: int = -1
    project_id: int = -1
    tags: List[str] = None

    def fromJson(self, jsonConfig) -> None:
        self.description = jsonConfig["data"]["description"]
        self.start = parser.parse(jsonConfig["data"]["start"])
        self.stop = parser.parse(jsonConfig["data"]["stop"])
        self.workspace_id = int(jsonConfig["data"]["wid"])
        self.project_id = int(jsonConfig["data"]["pid"])
        self.tags = jsonConfig["data"]["tags"]

    def toJson(self):
        returnJson =  {
            "time_entry": {
                "description": self.description,
                "wid": self.workspace_id,
                "pid": self.project_id
            }
        }
        if self.start is not None:
            returnJson["time_entry"]["stop"] = self.start.isoformat()
        if self.stop is not None:
            returnJson["time_entry"]["stop"] = self.stop.isoformat()
        if self.tags is not None:
            returnJson["time_entry"]["tags"] = self.tags

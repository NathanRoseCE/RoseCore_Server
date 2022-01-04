from dataclasses import dataclass
from datetime import datetime
from typing import List
import json
from dateutil import parser


@dataclass
class TimeEntry:
    id: int = -1
    description : str = ""
    start: datetime = None
    stop: datetime = None
    workspace_id: int = -1
    project_id: int = -1
    tags: List[str] = None
    synced: bool = True
    to_delete: bool = False

    def fromJson(self, jsonConfig) -> None:
        self.description = jsonConfig["description"]
        self.start = parser.parse(jsonConfig["start"])
        self.stop = parser.parse(jsonConfig["stop"])
        self.workspace_id = int(jsonConfig["wid"])
        self.project_id = int(jsonConfig["pid"])
        self.tags = jsonConfig["tags"]

    def toJson(self):
        returnJson =  {
            "description": self.description,
            "wid": self.workspace_id,
            "pid": self.project_id
        }
        if self.start is not None:
            returnJson["time_entry"]["stop"] = self.start.isoformat()
        if self.stop is not None:
            returnJson["time_entry"]["stop"] = self.stop.isoformat()
        if self.tags is not None:
            returnJson["time_entry"]["tags"] = self.tags

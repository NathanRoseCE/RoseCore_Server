from dataclasses import dataclass
from datetime import datetime
from typing import List
import json
from dateutil import parser
import pytz

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
        if "pid" in jsonConfig:
            self.project_id = int(jsonConfig["pid"])
        if self.start.tzinfo is None or self.start.tzinfo.utcoffset(self.start) is None:
            self.start = pytz.utc.localize(self.start)
        if self.stop.tzinfo is None or self.stop.tzinfo.utcoffset(self.stop) is None:
            self.stop = pytz.utc.localize(self.stop)
        self.tags = jsonConfig["tags"]

    def toJson(self):
        returnJson =  {
            "description": self.description,
            "pid": self.project_id,
            "created_with": "rosecore"
        }
        if self.start is not None:
            if self.start.tzinfo is None or self.start.tzinfo.utcoffset(self.start) is None:
                self.start = pytz.utc.localize(self.start)
            returnJson["start"] = self.start.isoformat("T", "milliseconds")
            returnJson["duration"] = 12
        if self.stop is not None:
            if self.stop.tzinfo is None or self.stop.tzinfo.utcoffset(self.stop) is None:
                self.stop = pytz.utc.localize(self.stop)
            returnJson["stop"] = self.stop.isoformat("T", "milliseconds")
        if self.tags is not None:
            returnJson["tags"] = self.tags
        return returnJson

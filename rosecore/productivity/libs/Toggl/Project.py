from dataclasses import dataclass


@dataclass
class Project:
    """
    A dataclass that holds relevant toggl information for Rosecore
    """
    name: str = ""
    id: int = -1
    workspace_id: int = -1
    active: bool = True
    to_delete = False
    synced = False

    def fromJson(self, jsonConfig) -> None:
        """
        initializes the dataclass from a json
        """
        self.name = jsonConfig["name"]
        self.id = jsonConfig["id"]
        self.workspace_id = jsonConfig["wid"]
        self.active = jsonConfig["active"]

    def toJson(self):
        return {
            "name": self.name,
            "id": self.id,
            "wid": self.workspace_id,
            "active": self.active
        }


class InvalidProject(Exception):
    def __init__(self, field, value):
        self.fieldName = field
        self.fieldValue = value

    def __str__(self) -> str:
        return f'Project is invalid: {self.fieldName} cannot be {self.fieldValue}'


class APIThrottled(Exception):
    def __str__(self) -> str:
        return 'API was throttled'

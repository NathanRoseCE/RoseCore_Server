class APIThrottled(Exception):
    def __str__(self) -> str:
        return 'API was throttled'

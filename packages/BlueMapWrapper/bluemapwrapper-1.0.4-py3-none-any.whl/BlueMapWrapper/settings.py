class Settings:
    """Get the settings of a map"""
    def __init__(self, version:str, maps:list):
        self.version = version
        self.maps = maps

    @staticmethod
    def from_response(settings_json: dict) -> "Settings":
        """Create a Settings Object from settings.json"""
        version = settings_json["version"]
        maps = settings_json["maps"]
        return Settings(version, maps)

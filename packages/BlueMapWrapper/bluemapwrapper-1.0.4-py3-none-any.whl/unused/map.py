class Map:
    def __init__(self, configName: str, name: str=None):
        self.configName = configName
        self.name = name

    def _from_response(self, response: dict) -> "Map":
        self.name = response["name"]
        return self



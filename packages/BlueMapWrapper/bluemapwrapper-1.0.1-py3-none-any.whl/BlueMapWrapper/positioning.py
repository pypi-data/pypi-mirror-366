class Position:
    """Set of Coordinates for a Player or Marker Object"""
    def __init__(self, x:float, y:float, z:float):
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def _from_response(response: dict) -> "Position":
        """Create a Coordinate Object from players.json or markers.json."""
        if 'y' not in response:
            response['y'] = 0
        return Position(response['x'], response['y'], response['z'])

class Rotation:
    """Rotation of Player Head"""
    def __init__(self, pitch:float, roll:float, yaw:float):
        self.pitch = pitch
        self.roll = roll
        self.yaw = yaw

    @staticmethod
    def _from_response(response: dict) -> "Rotation":
        """Create a Rotation Object from players.json. Response obtained from players.json -> player -> rotation"""
        return Rotation(response['pitch'], response['roll'], response['yaw'])
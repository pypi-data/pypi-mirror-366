from typing import Union
from .MarkerSet import MarkerSet
from .player import Player
from .exceptions import MultipleMatches


class MarkerCollection:
    """Collection of MarkerSets"""
    def __init__(self, marker_sets: list[MarkerSet]):
        self.marker_sets = marker_sets
        self.length = len(self.marker_sets)
        self._idx = 0

    def __iter__(self):
        self._idx = 0
        return self

    def __next__(self) -> Union[MarkerSet, None]:
        if self._idx >= self.length:
            raise StopIteration
        value = self.marker_sets[self._idx]
        self._idx += 1
        return value

    def __getitem__(self,idx) -> Union[MarkerSet, None]:
        return self.marker_sets[idx]

    @staticmethod
    def _from_response(response: dict) -> Union["MarkerCollection", None]:
        """Create a MarkerCollection Object from markers.json"""
        return MarkerCollection([MarkerSet._from_response(key, item) for key, item in response.items()])

    def from_key(self, key:str) -> Union[MarkerSet, None]:
        """Get a MarkerSet by its name. Use BlueMapWrapper.marker_keys for plugins"""
        matches = [i for i in self.marker_sets if i.key == key]
        if not matches:
            return None
        if len(matches) > 1:
            raise MultipleMatches(key)
        return matches[0]

class PlayerCollection:
    """Collection of Players"""
    def __init__(self, players: list[Player]):
        self.players = players
        self.length = len(players)
        self._idx = 0

    def __iter__(self):
        self._idx = 0
        return self

    def __next__(self) -> Union[Player, None]:
        if self._idx >= self.length:
            raise StopIteration
        value = self.players[self._idx]
        self._idx += 1
        return value

    def __getitem__(self,idx) -> Union[Player, None]:
        return self.players[idx]

    @staticmethod
    def _from_response(response: dict) -> Union["PlayerCollection", None]:
        """Create a PlayerCollection Object from players.json"""
        players = response['players']
        return PlayerCollection([Player._from_response(item) for item in players])

    def is_foreign(self) -> list[Union[Player, None]]:
        """Get a list of players who have the foreign attribute (not in the world requested)"""
        return [i for i in self.players if i.foreign]

    def not_foreign(self) -> list[Union[Player, None]]:
        """Get a list of players who do not have the foreign attribute (in the world requested)"""
        return [i for i in self.players if not i.foreign]

    def from_uuid(self, uuid:str) -> Union[Player, None]:
        """Get a Player Object by uuid"""
        matches = [i for i in self.players if i.uuid == uuid]
        if not matches:
            return None
        if len(matches) > 1:
            raise MultipleMatches(uuid)
        return matches[0]

    def from_name(self, name:str) -> Union[Player, None]:
        """Get a Player Object by name"""
        matches = [i for i in self.players if i.name.lower() == name.lower()]
        if not matches:
            return None
        if len(matches) > 1:
            raise MultipleMatches(name)
        return matches[0]

class Collection:
    """Collection of PlayerCollection and MarkerCollection"""
    def __init__(self, marker_collection: MarkerCollection, player_collection: PlayerCollection):
        self.marker_collection = marker_collection
        self.player_collection = player_collection

    @staticmethod
    def _from_response(marker_response: dict, player_response: dict) -> "Collection":
        """Get a Collection Object from markers.json and players.json"""
        marker_collection = MarkerCollection._from_response(marker_response)
        player_collection = PlayerCollection._from_response(player_response)
        return Collection(marker_collection, player_collection)
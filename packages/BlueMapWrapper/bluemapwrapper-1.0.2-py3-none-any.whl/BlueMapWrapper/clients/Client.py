import requests
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Text, Union
from ..settings import Settings
from ..Collections import MarkerCollection, PlayerCollection, Collection

class Client:
    """Synchronous Client for BlueMap"""
    def __init__(self, base_url:str):
        self.base_url = base_url

    def _get_markers_json(self, world:str) -> Dict:
        """Get a markers.json response from the API."""
        markers_link = f"{self.base_url}/maps/{world}/live/markers.json"
        markers_response = self._get_json(markers_link)
        return markers_response

    def _get_players_json(self, world:str) -> Dict:
        """Get a players.json response from the API."""
        players_link = f"{self.base_url}/maps/{world}/live/players.json"
        players_response = self._get_json(players_link)
        return players_response

    def fetch_maps(self) -> List[Union[Text, None]]:
        """Get a list of available maps from the API."""
        settings_link = f"{self.base_url}/settings.json"
        settings_response = self._get_json(settings_link)
        settings = Settings.from_response(settings_response)
        return settings.maps

    def fetch_marker_collection(self, world:str) -> MarkerCollection:
        """Get a MarkerCollection Object from markers.json response"""
        markers_response = self._get_markers_json(world)
        marker_collection = MarkerCollection._from_response(markers_response)
        return marker_collection

    def fetch_player_collection(self, world:str) -> PlayerCollection:
        """Get a PlayerCollection Object from players.json response"""
        players_response = self._get_players_json(world)
        players_collection = PlayerCollection._from_response(players_response)
        return players_collection

    def fetch_collection(self, world:str) -> Collection:
        """Get a Collection Object with both players.json and markers.json responses.
        Get PlayerCollection Object with Collection.player_collection
        Get MarkerCollection Object with Collection.marker_collection"""
        with ThreadPoolExecutor(max_workers=2) as executor:
            markers = executor.submit(self.fetch_marker_collection, world)
            players = executor.submit(self.fetch_player_collection, world)
        collection = Collection(markers.result(), players.result())
        return collection

    @staticmethod
    def _get_json(url:str, headers:dict=None, json:dict=None) -> Dict:
        """Get a JSON response from a request"""
        with requests.get(url, headers=headers, json=json) as response:
            response.raise_for_status()
            return response.json()
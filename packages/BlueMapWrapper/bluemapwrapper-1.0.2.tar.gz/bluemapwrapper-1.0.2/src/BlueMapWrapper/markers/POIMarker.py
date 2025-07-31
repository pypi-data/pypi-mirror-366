from __future__ import annotations
from ..positioning import Position

if annotations:
    from .BaseMarker import BaseMarker

class POIMarker(BaseMarker):
    """A POI Marker is a single labeled point on a map"""
    def __init__(self, key: str, label: str, position:Position, detail:str=None, icon:str=None, classes:list=None):
        super().__init__(key,label, position)
        self.detail = detail
        self.icon = icon
        self.classes = classes

    @staticmethod
    def _from_response(response: tuple) -> "POIMarker":
        """Create a POIMarker object from markers.json.
        Response obtained from markers.json -> MarkerSet -> Markers -> POIMarker"""
        key = response[0]
        response = response[1]
        label = response['label']
        position = Position._from_response(response['position'])
        detail = response['detail']
        icon = response['icon']
        classes = response['classes']
        return POIMarker(key, label, position, detail, icon, classes)
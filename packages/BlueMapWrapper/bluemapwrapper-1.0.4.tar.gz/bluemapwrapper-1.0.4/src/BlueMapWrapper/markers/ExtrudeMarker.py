from __future__ import annotations
from typing import Optional
from ..positioning import Position
if annotations:
    from .BaseMarker import BaseMarker

class ExtrudeMarker(BaseMarker):
    """An Extrude Marker is a 3D shape"""
    def __init__(self, key: str, label: str, position: Position, shape:list[Position], shape_min_y:int, shape_max_y:int, detail:Optional[str]=None):
        super().__init__(key, label, position)
        self.shape = shape
        self.shape_min_y = shape_min_y
        self.shape_max_y = shape_max_y
        self.detail = detail

    @staticmethod
    def _from_response(response: tuple) -> "ExtrudeMarker":
        """Create an ExtrudeMarker object from markers.json.
        Response obtained from markers.json -> MarkerSet -> Markers -> ExtrudeMarker"""
        key = response[0]
        response = response[1]
        label = response['label']
        position = Position._from_response(response['position'])
        shape = [Position._from_response(i) for i in response['shape']]
        shape_min_y = response['shape-min-y']
        shape_max_y = response['shape-max-y']
        detail = response['detail']
        return ExtrudeMarker(key, label, position, shape, shape_min_y, shape_max_y, detail=detail)

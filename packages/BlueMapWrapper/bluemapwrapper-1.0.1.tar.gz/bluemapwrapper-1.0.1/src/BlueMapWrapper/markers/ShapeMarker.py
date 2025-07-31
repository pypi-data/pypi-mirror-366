from __future__ import annotations
from ..positioning import Position
if annotations:
    from .BaseMarker import BaseMarker

class ShapeMarker(BaseMarker):
    """A Shape marker is a 2D plane on a map"""
    def __init__(self, key: str, label: str, position: Position, shape:list[Position], shape_y:int, detail:str=None):
        super().__init__(key, label, position)
        self.shape = shape
        self.shape_y = shape_y
        self.detail = detail

    @staticmethod
    def _from_response(response: tuple) -> "ShapeMarker":
        """Create a ShapeMarker object from markers.json.
        Response obtained from markers.json -> MarkerSet -> Markers -> ShapeMarker"""
        key = response[0]
        response = response[1]
        label = response['label']
        position = Position._from_response(response['position'])
        shape = [Position._from_response(i) for i in response['shape']]
        shape_y = response['shape-y']
        detail = response['detail']
        return ShapeMarker(key, label, position, shape, shape_y, detail=detail)
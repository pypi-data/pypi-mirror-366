from __future__ import annotations
from ..positioning import Position
if annotations:
    from .BaseMarker import BaseMarker

class LineMarker(BaseMarker):
    """A Line marker is a line consisting of atleast 2 coordinates"""
    def __init__(self, key: str, label: str, position: Position, line:list[Position], detail:str=None):
        super().__init__(key, label, position)
        self.line = line
        self.detail = detail

    @staticmethod
    def _from_response(response: tuple) -> "LineMarker":
        """Create a LineMarker object from markers.json.
                Response obtained from markers.json -> MarkerSet -> Markers -> LineMarker"""
        key = response[0]
        response = response[1]
        label = response['label']
        position = Position._from_response(response['position'])
        line = response['line']
        detail = response['detail']
        return LineMarker(key, label, position, line, detail=detail)
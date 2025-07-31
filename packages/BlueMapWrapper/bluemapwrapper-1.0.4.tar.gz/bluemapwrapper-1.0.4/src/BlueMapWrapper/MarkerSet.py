from __future__ import annotations
from typing import Union
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable
from .markers.markers import get_markers
from .markers import HTMLMarker, ShapeMarker, ExtrudeMarker, LineMarker, POIMarker
if annotations:
    pass


class MarkerSet:
    """A Set of Markers, usually from a plugin"""
    def __init__(self, key:str, label:str, markers:list):
        self.key = key
        self.label = label
        self.markers = markers
        self.length = len(markers)
        self._index = 0

    def __iter__(self):
        self._idx = 0
        return self

    def __next__(self) -> Union[MarkerSet, None]:
        if self._idx >= self.length:
            raise StopIteration
        value = self.markers[self._idx]
        self._idx += 1
        return value

    def __getitem__(self,idx) -> Union[MarkerSet, None]:
        return self.markers[idx]

    @staticmethod
    def _from_response(key:str, response_json: dict) -> Union["MarkerSet", None]:
        """Get a MarkerSet from markers.json"""
        if not response_json: return None
        label = response_json["label"]
        unformattedMarkers = response_json["markers"]
        with ThreadPoolExecutor() as executor:
            markers = list(executor.map(get_markers, [i for i in unformattedMarkers.items()]))
        return MarkerSet(key, label, markers)

    def extrude_markers(self) -> Iterable[Union[ExtrudeMarker, None]]:
        """Return a list of ExtrudeMarkers within self.markers"""
        return [i for i in self.markers if isinstance(i, ExtrudeMarker)]

    def html_markers(self) -> Iterable[Union[HTMLMarker, None]]:
        """Return a list of HTMLMarkers within self.markers"""
        return [i for i in self.markers if isinstance(i, HTMLMarker)]

    def line_markers(self) -> Iterable[Union[LineMarker, None]]:
        """Return a list of LineMarkers within self.markers"""
        return [i for i in self.markers if isinstance(i, LineMarker)]

    def poi_markers(self) -> Iterable[Union[POIMarker, None]]:
        """Return a list of POIMarkers within self.markers"""
        return [i for i in self.markers if isinstance(i, POIMarker)]

    def shape_markers(self) -> Iterable[Union[ShapeMarker, None]]:
        """Return a list of ShapeMarkers within self.markers"""
        return [i for i in self.markers if isinstance(i, ShapeMarker)]



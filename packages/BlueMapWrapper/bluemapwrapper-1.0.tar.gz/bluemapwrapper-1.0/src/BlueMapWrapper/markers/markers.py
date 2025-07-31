from __future__ import annotations
from typing import Union

if annotations:
    from .ExtrudeMarker import ExtrudeMarker
    from .HTMLMarker import HTMLMarker
    from .POIMarker import POIMarker
    from .LineMarker import LineMarker
    from .ShapeMarker import ShapeMarker

markerTypes = {'poi': POIMarker,
               'html': HTMLMarker,
               'line': LineMarker,
               'shape': ShapeMarker,
               'extrude': ExtrudeMarker}

def get_markers(response:tuple) -> Union[POIMarker, HTMLMarker, LineMarker, ShapeMarker, ExtrudeMarker]:
    """Identify and create a Marker Object based on its type.
    Response obtained from markers.json -> MarkerSet -> Markers -> Marker"""
    key = response[0]
    marker_type = response[1]['type']
    return markerTypes[marker_type]._from_response((key, response[1]))
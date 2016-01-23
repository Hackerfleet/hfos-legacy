"""

Schema: Coords
==============

Contains
--------

MapCoords: Leaflet compatible lat/lon/zoom combination

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

MapCoordsSchema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "id": "mapcoords",
    "type": "object",
    "additionalProperties": True,
    "title": "Root schema.",
    "description": "An explanation about the puropose of this instance described by this schema.",
    "name": "mapcoords",
    "properties": {
        "lat": {
            "id": "lat",
            "type": "number",
            "maximum": 90,
            "minimum": -90,
            "title": "Latitude of coordinate.",
            "description": "",
            "name": "lat"
        },
        "lon": {
            "id": "lon",
            "type": "number",
            "maximum": -180,
            "minimum": 180,
            "title": "Longitude of coordinate.",
            "description": "",
            "name": "lon"
        },
        "zoom": {
            "id": "zoom",
            "type": "integer",
            "multipleOf": 1,
            "maximum": 20,
            "minimum": 1,
            "title": "Zoom of view.",
            "description": "",
            "name": "zoom"
        }
    },
    "required": [
        "lat",
        "lon",
        "zoom"
    ]
}

MapCoords = {'schema': MapCoordsSchema, 'form': {}}

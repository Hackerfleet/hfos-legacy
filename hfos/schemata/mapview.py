"""
Hackerfleet Operating System - Backend

Schema: Mapview
=================

Contains
========

MapView: User generated Mapviews

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

# {
#     'type': "object",
#     'name': 'Profile',
#     'properties': {
#         'name': {'type': "string", 'minLength': 2, 'title': "Name", 'description': "Name or alias"},
#         'title': {
#             'type': "string",
#             'enum': ['dr','jr','sir','mrs','mr','NaN','dj']
#         }
#     }
# }

MapView = {
    'type': 'object',
    'id': '#mapview',
    'name': 'Mapview',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36, 'title': 'Unique Mapview ID', 'description': 'HIDDEN'},
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name', 'description': 'Name of view'},
        'color': {'type': 'string', 'title': 'View Color', 'format': 'color',
                  'description': 'This views color indicator'},
        'shared': {'type': 'boolean', 'title': 'Shared view', 'description': 'Share view with the crew'},
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes', 'description': 'Custom user notes'},
        'coords': {
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
            },
            "autoDiscover": {
                "id": "autoDiscover",
                "type": "boolean",
                "title": "Autodiscover on device.",
                "description": "",
                "name": "autoDiscover"
            }

        }
    },
    "required": [
        'uuid'
    ]
}

__schema__ = MapView
"""

Schema: Mapview
===============

Contains
--------

MapView: User generated Mapviews

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

# {
# 'type': "object",
# 'name': 'Profile',
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
        'uuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                 'type': 'string',
                 'title': 'Unique Mapview ID'
                 },
        'useruuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                     'type': 'string',
                     'title': "Owner's unique user ID"
                     },
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name', 'description': 'Name of view'},
        'color': {'type': 'string', 'title': 'View Color', 'format': 'color',
                  'description': 'This views color indicator'},
        'shared': {'type': 'boolean', 'title': 'Shared', 'description': 'Share mapview with the crew'},
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes', 'description': 'Custom user notes'},
        'layergroups': {'type': 'array',
                        'items': {
                            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                            'type': 'string',
                            'title': 'Unique Layergroup ID'
                        }
                        },
        'coords': {
            "lat": {
                "id": "lat",
                "type": "number",
                "maximum": 90,
                "minimum": -90,
                "title": "Latitude of coordinate.",
                "description": "",
                "name": "lat",
                "default": 54.17805
            },
            "lon": {
                "id": "lon",
                "type": "number",
                "maximum": -180,
                "minimum": 180,
                "title": "Longitude of coordinate.",
                "description": "",
                "name": "lon",
                "default": 7.88669
            },
            "zoom": {
                "id": "zoom",
                "type": "integer",
                "multipleOf": 1,
                "maximum": 20,
                "minimum": 1,
                "title": "Zoom of view.",
                "description": "",
                "name": "zoom",
                "default": 16
            },
            "autoDiscover": {
                "id": "autoDiscover",
                "type": "boolean",
                "title": "Autodiscover on device.",
                "description": "",
                "name": "autoDiscover",
                "default": True
            }

        }
    },
    "required": [
        'uuid'
    ]
}

__schema__ = MapView

"""

Schema: Mapview
===============

Contains
--------

MapView: User generated Mapviews

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""
from hfos.schemata.defaultform import defaultform
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

MapViewSchema = base_object('mapview',
                            roles_read=['owner', 'admin', 'crew'],
                            roles_write=['owner', 'admin', 'navigator'],
                            roles_create=['admin', 'navigator'],
                            roles_list=['owner', 'admin', 'crew']
                            )

MapViewSchema['properties'].update({
    'owner': {
        'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                   'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
        'type': 'string',
        'title': "Owner's unique user ID"
    },
    'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
             'description': 'Name of view'},
    'color': {'type': 'string', 'title': 'View Color', 'format': 'color',
              'description': 'This views color indicator'},
    'shared': {'type': 'boolean', 'title': 'Shared',
               'description': 'Share mapview with the crew'},
    'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
              'description': 'Custom user notes'},
    'viewtype': {'enum': ['vessel', 'user'], 'title': 'View Type',
                 'description': 'Shows what type of mapview this is'},
    'layergroups': {
        'type': 'array',
        'items': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
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
        "lng": {
            "id": "lng",
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
})

MapView = {'schema': MapViewSchema, 'form': defaultform}

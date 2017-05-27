"""

Schema: Mapview
===============

Contains
--------

MapView: User generated Mapviews

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""
from hfos.schemata.defaultform import lookup_field, editbuttons
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

MapViewSchema = base_object('mapview',
                            roles_read=['crew'],
                            roles_write=['navigator', 'crew'],
                            roles_create=['navigator', 'crew'],
                            roles_list=['crew']
                            )

MapViewSchema['properties'].update({
    'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
             'description': 'Name of view'},
    'color': {'type': 'string', 'title': 'View Color', 'format': 'color',
              'description': 'This views color indicator'},
    'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
              'description': 'Custom user notes'},
    'viewtype': {'enum': ['vessel', 'user'], 'title': 'View Type',
                 'description': 'Shows what type of mapview this is'},
    'layergroups': {
        'type': 'array',
        'description': 'List of available Layergroups',
        'items': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Layergroup',
            'description': 'Select a Layergroup'
        },
        'default': []
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

MapViewForm = [
    'name',
    'color',
    'notes',
    {
        'key': 'layergroups',
        'validationMessage': ' ',
        'disableErrorState': True,
        'items': [
            lookup_field('layergroups[]', 'layergroup'),
        ]
    },
    editbuttons
]

MapView = {'schema': MapViewSchema, 'form': MapViewForm}

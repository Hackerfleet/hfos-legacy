"""

Schema: Geoobject
=================

Contains
--------

Geoobject: General geoobject configuration data encapsulating geojson

See also
--------

Provisions

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import defaultform

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

GeoObjectSchema = {
    'type': 'object',
    'id': '#geoobject',
    'name': 'geoobject',
    'properties': {
        'uuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique GeoObject ID'
        },
        'layer': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique GeoObject Layer ID'
        },
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
                 'description': 'Name of GeoObject'},
        'owner': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique GeoObject Owner ID'
        },
        'color': {'type': 'string', 'title': 'GeoObject Color', 'format':
            'color',
                  'description': 'This GeoObject color indicator'},
        'shared': {'type': 'boolean', 'title': 'Shared GeoObject',
                   'description': 'Share GeoObject with the crew'},
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                  'description': 'Custom user notes'},
        'minZoom': {'type': 'number', 'description': 'Minimum zoom number.',
                    'default': 0},
        'maxZoom': {'type': 'number', 'description': 'Maximum zoom number.',
                    'default': 18},
        'opacity': {'type': 'number',
                    'description': 'The opacity of the GeoObject.',
                    'default': 1.0},
        'zIndex': {'type': 'number',
                   'description': 'The explicit zIndex of the GeoObject.'
                                  'Not set by default.',
                   },

        'geojson': {
            'type': 'object',
            'default': {},
            'properties': {}
        }
    }
}

GeoObject = {'schema': GeoObjectSchema, 'form': defaultform}

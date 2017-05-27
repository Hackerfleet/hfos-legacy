"""

Schema: Geoobject
=================

Contains
--------

Geoobject: General geoobject configuration data encapsulating geojson

See also
--------

Provisions

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import defaultform
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

GeoObjectSchema = base_object('geoobject', all_roles='crew')

GeoObjectSchema['properties'].update({
    'layer': {
        'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                   'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
        'type': 'string',
        'title': 'Unique GeoObject Layer ID'
    },
    'color': {'type': 'string', 'title': 'Background Color',
              # 'format': 'color',
              'description': 'GeoObject background color indicator',
              'default': '#4384BF'},
    'iconcolor': {'type': 'string', 'title': 'Icon Color',
                  # 'format': 'color',
                  'description': 'GeoObject icon color indicator', 'default':
                      'white'},
    'icon': {'type': 'string', 'title': 'Icon',
             'description': 'Custom user icon', 'default': 'flag'},
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
)
GeoObject = {'schema': GeoObjectSchema, 'form': defaultform}

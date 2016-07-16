"""

Schema: LayerGroup
==================

Contains
--------

LayerGroup: A configurable group of predefined layers

See also
--------

Provisions

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import defaultform

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

LayerGroupSchema = {
    'type': 'object',
    'id': '#layergroup',
    'name': 'layergroup',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36, 'title': 'Unique Group ID',
                 'description': 'HIDDEN'},
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
                 'description': 'Name of Group'},
        'owner': {'type': 'string', 'minLength': 36,
                  'title': "Owner's Unique ID", 'description': 'HIDDEN'},
        'color': {'type': 'string', 'title': 'Group Color', 'format': 'color',
                  'description': 'This group''s color indicator'},
        'shared': {'type': 'boolean', 'title': 'Shared group',
                   'description': 'Share group with the crew'},
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                  'description': 'Custom user notes'},
        'layers': {
            'type': 'array',
            'items': {
                'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-['
                           'a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{'
                           '12}$',
                'type': 'string',
                'title': 'Unique Layer ID'
            }
        }
    }
}

LayerGroup = {'schema': LayerGroupSchema, 'form': defaultform}

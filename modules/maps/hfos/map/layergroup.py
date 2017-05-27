"""

Schema: LayerGroup
==================

Contains
--------

LayerGroup: A configurable group of predefined layers

See also
--------

Provisions

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import editbuttons
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

LayerGroupSchema = base_object('layergroup',
                               roles_read=['crew'],
                               roles_write=['navigator'],
                               roles_create=['navigator'],
                               roles_list=['crew']
                               )

LayerGroupSchema['properties'].update({
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
})

LayerGroupForm = [
    'name',
    'notes',
    {
        'key': 'layers',
        'add': "Add layer",
        'style': {
            'add': "btn-success"
        },
        'items': [
            {
                'key': 'layers[]',
                'type': 'strapselect',
                'placeholder': 'Select a Layer',
                'options': {
                    "type": "layer",
                    "asyncCallback": "$ctrl.getFormData",
                    "map": {'valueProperty': "uuid", 'nameProperty': 'name'}
                }
            }
        ]
    },
    editbuttons
]

LayerGroup = {'schema': LayerGroupSchema, 'form': LayerGroupForm}

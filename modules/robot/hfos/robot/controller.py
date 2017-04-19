"""

Schema: Controller
==================

Contains
--------

Controller: Remote control input device to controllable mapping

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import defaultform
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

ControllerSchema = base_object('controller')

ControllerSchema['properties'].update({
    'description': {'type': 'string'},
    'mappings': {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'controltype': {'enum': ['analog', 'digital']},
                'controlaxis': {'type': 'integer'},
                'controlbutton': {'type': 'integer'},
                'controluuid': {
                    'pattern':
                        '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-['
                        'a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                        'a-fA-F0-9]{12}$',
                    'type': 'string',
                    'title': 'Associated uuid of Controllable'
                },
            }
        }
    }
})

Controller = {'schema': ControllerSchema, 'form': defaultform}

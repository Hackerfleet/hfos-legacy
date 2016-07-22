"""

Schema: Controller
==================

Contains
--------

Controller: Remote control input device to controllable mapping

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from hfos.schemata.defaultform import defaultform

ControllerSchema = {
    'id': '#controller',
    'type': 'object',
    'name': 'controller',
    'properties': {
        'uuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique Controller Configuration ID'
            },
        'name': {'type': 'string'},
        'description': {'type': 'string'},
        'mappings': {'type': 'array',
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

    }
}

Controller = {'schema': ControllerSchema, 'form': defaultform}

"""
Schema: Controllable
====================

Contains
--------

Controllable: Patterns of remote control

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import defaultform

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

ControllableSchema = {
    'id': '#controllable',
    'type': 'object',
    'name': 'controllable',
    'properties': {
        'uuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique Controllable ID'
            },
        'name': {'type': 'string'},
        'description': {'type': 'string'},
        'type': {'enum': ['analog', 'digital']},
        'min': {'type': 'integer', 'default': 0},
        'center': {'type': 'integer', 'default': 127},
        'max': {'type': 'integer', 'default': 255},
    }
}

Controllable = {'schema': ControllableSchema, 'form': defaultform}

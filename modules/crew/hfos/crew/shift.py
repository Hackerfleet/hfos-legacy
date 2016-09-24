"""
Schema: Shift
=============

Contains
--------

Shift: Stores shift information for timetables and assisted rotation

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import *

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

ShiftSchema = {
    'id': '#shiftconfig',
    'type': 'object',
    'name': 'shiftconfig',
    'properties': {
        'uuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique Shift ID'
        },
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
                 'description': 'Shift name'},
        'locked': {'type': 'boolean', 'title': 'Locked Shift',
                   'description': 'Determines whether the Shift should '
                                  'be locked against changes.'},
        'description': {'type': 'string', 'format': 'html',
                        'title': 'Shift description',
                        'description': 'Shift description'},
        'useruuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Associated Unique User ID'
        }
    },
    "required": [
        'uuid'
    ]
}

ShiftForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'name'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'shared', 'locked'
                ]
            },
        ]
    },
    'description',
    editbuttons
]

ShiftConfig = {'schema': ShiftSchema, 'form': ShiftForm}

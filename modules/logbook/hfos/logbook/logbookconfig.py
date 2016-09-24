"""
Schema: Logbookconfig
=====================

Contains
--------

Logbook: Structure to store logbook configurations

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import *

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

LogbookSchema = {
    'id': '#logbookconfig',
    'type': 'object',
    'name': 'logbookconfig',
    'properties': {
        'uuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique Logbook ID'
        },
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
                 'description': 'Logbook name'},
        'locked': {'type': 'boolean', 'title': 'Locked Logbook',
                   'description': 'Determines whether the Logbook should '
                                  'be locked against changes.'},
        'shared': {'type': 'boolean', 'title': 'Shared Logbook',
                   'description': 'Share Logbook with the crew'},
        'description': {'type': 'string', 'format': 'html',
                        'title': 'Logbook description',
                        'description': 'Logbook description'},
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

LogbookForm = [
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

LogbookConfig = {'schema': LogbookSchema, 'form': LogbookForm}

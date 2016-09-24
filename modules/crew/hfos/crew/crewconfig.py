"""
Schema: Crewconfig
==================

Contains
--------

crewconfig: Structure to store information about crews, for timetable and other useful features

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import *

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

CrewSchema = {
    'id': '#crewconfig',
    'type': 'object',
    'name': 'crewconfig',
    'properties': {
        'uuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique Crew ID'
        },
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
                 'description': 'Crew name'},
        'locked': {'type': 'boolean', 'title': 'Locked Crew',
                   'description': 'Determines whether the Crew should '
                                  'be locked against changes.'},
        'shared': {'type': 'boolean', 'title': 'Shared Crew',
                   'description': 'Share Crew with the crew'},
        'description': {'type': 'string', 'format': 'html',
                        'title': 'Crew description',
                        'description': 'Crew description'},
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

CrewForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'name',
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

CrewConfig = {'schema': CrewSchema, 'form': CrewForm}

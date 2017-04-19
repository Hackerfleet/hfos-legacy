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
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

CrewSchema = base_object('crewconfig')

CrewSchema['properties'].update({
    'locked': {'type': 'boolean', 'title': 'Locked Crew',
               'description': 'Determines whether the Crew should '
                              'be locked against changes.'},
    'shared': {'type': 'boolean', 'title': 'Shared Crew',
               'description': 'Share Crew with the crew'},
    'description': {'type': 'string', 'format': 'html',
                    'title': 'Crew description',
                    'description': 'Crew description'},
})

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

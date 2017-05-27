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
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

LogbookSchema = base_object('logbookconfig', all_roles='crew')

LogbookSchema['properties'].update({
    'locked': {
        'type': 'boolean', 'title': 'Locked Logbook',
        'description': 'Determines whether the Logbook should '
                       'be locked against changes.'
    },
    'shared': {
        'type': 'boolean', 'title': 'Shared Logbook',
        'description': 'Share Logbook with the crew'
    },
    'description': {
        'type': 'string', 'format': 'html',
        'title': 'Logbook description',
        'description': 'Logbook description'
    }
})

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

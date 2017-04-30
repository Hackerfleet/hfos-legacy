"""
Schema: Automatconfig
=====================

Contains
--------

Automat: Structure to store automat configurations

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import *
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

AutomatSchema = base_object('automatconfig')
AutomatSchema['properties'].update({
    'locked': {
        'type': 'boolean', 'title': 'Locked Automat',
        'description': 'Determines whether the Automat should '
                       'be locked against changes.'
    },
    'description': {
        'type': 'string', 'format': 'html',
        'title': 'Automat description',
        'description': 'Automat description'
    }
})

AutomatForm = [
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
                    'locked'
                ]
            },
        ]
    },
    'description',
    editbuttons
]

AutomatConfig = {'schema': AutomatSchema, 'form': AutomatForm}

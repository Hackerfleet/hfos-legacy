"""
Schema: Taskgrid
=================

Contains
--------

Taskgrid: Taskgrid config to store gridster settings

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import *
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

TaskGridConfigSchema = base_object('taskgridconfig')

TaskGridConfigSchema['properties'].update({
    'locked': {'type': 'boolean', 'title': 'Locked Taskgrid',
               'description': 'Determines whether the Taskgrid should '
                              'be locked against changes.'},
    'shared': {'type': 'boolean', 'title': 'Shared Taskgrid',
               'description': 'Share Taskgrid with the crew'},
    'description': {'type': 'string', 'format': 'html',
                    'title': 'Taskgrid description',
                    'description': 'Taskgrid description'},
    'cards': {
        'type': 'array',
        'default': [],
        'items': {
            'type': 'object',
            'id': '#Card',
            'name': 'TaskGridCard',
            'properties': {
                'taskgroup': {
                    'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{'
                               '4}-['
                               'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                    'type': 'string',
                    'title': 'Associated Unique Task '
                             'Group ID'
                },
                'position': {
                    'type': 'object',
                    'properties': {
                        'x': {'type': 'number'},
                        'y': {'type': 'number'}
                    }
                },
                'size': {
                    'type': 'object',
                    'properties': {
                        'width': {'type': 'number'},
                        'height': {'type': 'number'}
                    }
                },
            }
        }
    }
})

TaskGridConfigForm = [
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
    {
        'key': 'cards',
        'add': "Add Task Group",
        'startEmpty': True,
        'style': {
            'add': "btn-success"
        },
        'items': [
            {
                'key': 'cards[].taskgroup',
                'type': 'strapselect',
                'placeholder': 'Select a Task Group',
                'options': {
                    "type": "taskgroup",
                    "asyncCallback": "$ctrl.getFormData",
                    "map": {'valueProperty': "uuid",
                            'nameProperty': 'name'}
                }
            }
        ]
    },
    'description',
    editbuttons
]

TaskGridConfig = {'schema': TaskGridConfigSchema, 'form': TaskGridConfigForm}

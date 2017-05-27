"""
Schema: Dashboard
=================

Contains
--------

Dashboard: Dashboard config to store gridster settings

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import *
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

DashboardSchema = base_object('dashboardconfig', all_roles='crew')

DashboardSchema['properties'].update({
    'locked': {'type': 'boolean', 'title': 'Locked Dashboard',
               'description': 'Determines whether the Dashboard should '
                              'be locked against changes.'},
    'refreshrate': {'title': 'Refreshrate', 'type': 'number',
                    'description': 'General refresh rate of dashboard'},
    'shared': {'type': 'boolean', 'title': 'Shared Dashboard',
               'description': 'Share Dashboard with the crew'},
    'description': {'type': 'string', 'format': 'html',
                    'title': 'Dashboard description',
                    'description': 'Dashboard description'},
    'cards': {
        'type': 'array',
        'default': [],
        'items': {
            'type': 'object',
            'id': '#Card',
            'name': 'DashboardCard',
            'properties': {
                'widgettype': {
                    'type': 'string',
                    'enum': [
                        'simplebarreadout',
                        'historybarreadout',
                        'digitalreadout',
                        'simplecompass'
                    ]
                },
                'valuetype': {'type': 'string'},
                'title': {'type': 'string'},
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
                        'width': {'type': 'number', 'default': 2},
                        'height': {'type': 'number', 'default': 2}
                    }
                },
            }
        }
    }
})

DashboardForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'name', 'refreshrate'
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
        'add': "Add widget",
        'style': {
            'add': "btn-success"
        },
        'items': [
            'cards[].title',
            'cards[].widgettype',
            {
                'key': 'cards[].valuetype',
                'type': 'strapselect',
                'placeholder': 'Select a Sensor Value',
                'options': {
                    "type": "sensordatatype",
                    "asyncCallback": "$ctrl.getFormData",
                    "map": {'valueProperty': "name", 'nameProperty':
                        'name'}
                }
            }

        ],
        'startEmpty': True,

    },
    'description',
    editbuttons
]

DashboardConfig = {'schema': DashboardSchema, 'form': DashboardForm}

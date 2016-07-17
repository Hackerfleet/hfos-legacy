"""
Schema: Dashboard
=================

Contains
--------

Dashboard: Dashboard config to store deckster settings

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import *

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

DashboardSchema = {
    'id': '#dashboardconfig',
    'type': 'object',
    'name': 'dashboardconfig',
    'properties': {
        'uuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique Dashboard ID'
        },
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
                 'description': 'Dashboard name'},
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
        'useruuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Associated Unique User ID'
        },
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
                            'digitalreadout'
                        ]
                    },
                    'valuetype': {'type': 'string'},
                    'title': {'type': 'string'},
                    'size': {
                        'type': 'object',
                        'properties': {
                            'x': {'type': 'number'},
                            'y': {'type': 'number'}
                        }
                    },
                    'position': {
                        'type': 'object',
                        'properties': {
                            'width': {'type': 'number'},
                            'height': {'type': 'number'}
                        }
                    },
                }
            }
        }
    },
    "required": [
        'uuid'
    ]
}

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
            'cards[].valuetype',
            {'type': 'section',
             'htmlClass': 'row',
             'items': [
                 {
                     'type': 'section',
                     'htmlClass': 'col-xs-4',
                     'items': [
                         'cards[].position'
                     ]
                 },
                 {
                     'type': 'section',
                     'htmlClass': 'col-xs-4',
                     'items': [
                         'cards[].size'
                     ]
                 }
             ]
             }
        ]
    },
    'description',
    editbuttons
]

DashboardConfig = {'schema': DashboardSchema, 'form': DashboardForm}

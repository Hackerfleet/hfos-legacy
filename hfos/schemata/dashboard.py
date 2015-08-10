"""
Schema: Dashboard
=================

Contains
--------

Dashboard: Dashboard config to store deckster settings

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from sensordata import SensorValueTypes

Dashboardconfig = {
    'id': '#Dashboard',
    'type': 'object',
    'name': 'Dashboard',
    'properties': {
        'uuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                 'type': 'string',
                 'title': 'Unique Dashboard ID'
                 },
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name', 'description': 'Dashboard name'},
        'locked': {'type': 'boolean', 'title': 'Locked Dashboard',
                   'description': 'Determines whether the Dashboard should be locked against changes.'},
        'description': {'type': 'string', 'format': 'html', 'title': 'Dashboard description',
                        'description': 'Dashboard description'},
        'useruuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                     'type': 'string',
                     'title': 'Associated Unique User ID'
                     },
        'cards': {'type': 'array',
                  'items': {
                      'type': 'object',
                      'id': '#Card',
                      'name': 'DashboardCard',
                      'properties': {
                          'id': {'type': 'string', 'enum': ['bearing', 'gauge', 'digital']},
                          'size': {'type': 'object',
                                   'properties': {
                                       'x': {'type': 'number'},
                                       'y': {'type': 'number'}
                                   }
                                   },
                          'position': {'type': 'array', 'items': {'type': 'number'}},
                          'value': {'type': 'string', 'enum': SensorValueTypes}
                      }
                  }
                  }
    }
}

DashboardconfigForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'name', 'theme'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    {'key': 'active', 'readonly': True}, 'locked'
                ]
            }
        ]
    },
    'description',
    {
        'type': 'submit',
        'title': 'Save Dashboard configuration',
    }
]

__schema__ = Dashboardconfig
__form__ = DashboardconfigForm

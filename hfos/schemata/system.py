"""
Schema: System
==============

Contains
--------

System: Global systemwide settings

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

Systemconfig = {
    'id': '#systemconfig',
    'type': 'object',
    'name': 'systemconfig',
    'properties': {
        'uuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                 'type': 'string',
                 'title': 'Unique System ID'
                 },
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name', 'description': 'System name'},
        'description': {'type': 'string', 'format': 'html', 'title': 'Description',
                        'description': 'System description'},
        'owneruuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                      'type': 'string',
                      'title': 'Associated Unique Owner User ID'
                      },
        'vesseluuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                       'type': 'string',
                       'title': 'Associated Unique Vessel ID'
                       },

        'defaultmapviewuuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Default Unique Mapview ID'
            },
        'defaultdashboarduuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Default Unique Dashboard ID'
            },
        'defaulttheme': {'type': 'string', 'title': 'Default new client theme',
                         'description': 'Default theme used for user interface'},
    }
}

SystemconfigForm = [
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
        'title': 'Save client configuration',
    }
]

__schema__ = Clientconfig
__form__ = ClientconfigForm

"""
Schema: Client
==============

Contains
--------

Client: Clientprofile to store client specific settings

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

Clientconfig = {
    'id': '#client',
    'type': 'object',
    'name': 'Client',
    'properties': {
        'uuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                 'type': 'string',
                 'title': 'Unique Client ID'
                 },
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name', 'description': 'Client name'},
        'active': {'type': 'boolean', 'title': 'Active client',
                   'description': 'Indicates whether client is currently active.'},
        'locked': {'type': 'boolean', 'title': 'Locked client',
                   'description': 'Determines whether the client should be locked against changes.'},
        'currentview': {'type': 'string', 'minLength': 1, 'title': 'Name', 'description': 'Client name'},
        'theme': {'type': 'string', 'title': 'Client Theme', 'description': 'Theme used for user interface'},
        'description': {'type': 'string', 'format': 'html', 'title': 'Client description',
                        'description': 'Client description'},
        'useruuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                     'type': 'string',
                     'title': 'Associated Unique User ID'
                     },
        'mapviewuuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                        'type': 'string',
                        'title': 'Associated Unique Mapview ID'
                        },
        'dashboarduuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                          'type': 'string',
                          'title': 'Associated Unique Dashboard ID'
                          }
    }
}

ClientconfigForm = [
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

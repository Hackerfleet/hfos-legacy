
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
        'clientuuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                       'type': 'string',
                       'title': 'Unique Client ID'
                       },
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name', 'description': 'Client name'},
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
    }
}

__schema__ = Clientconfig

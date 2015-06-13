"""

Schema: User
============

Account credentials and administrativa

Contains
--------

User: Useraccount object

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

User = {
    'id': '#user',
    'type': 'object',
    'name': 'User',
    'properties': {
        'username': {'type': 'string'},
        'passhash': {'type': 'string'},
        'groups': {'type': 'array',
                   'items': {
                       'type': 'number'
                   },
                   },
        'uuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                 'type': 'string',
                 'title': 'Unique User ID'
                 }
    }
}

__schema__ = User

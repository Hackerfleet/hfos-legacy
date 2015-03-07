"""
Hackerfleet Operating System - Backend

Schema: User
============

Account credentials and administrativa

Contains
========

User: Useraccount object

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

User = {
    'type': 'object',
    'name': 'User',
    'properties': {
        'username': {'type': 'string'},
        'passhash': {'type': 'string'},
        'groups': {'type': 'array', 'items': 'integer'},
        'uuid': {'type': 'string'}
    }
}
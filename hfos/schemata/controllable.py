"""
Hackerfleet Operating System - Backend

Schema: Profile
=================

Contains
========

Profile: Userprofile with general flags and fields

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

Controllable = {
    'id': '#controllable',
    'type': 'object',
    'name': 'Controllable',
    'properties': {
        'uuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                 'type': 'string',
                 'title': 'Unique Controllable ID'
                 },
        'name': {'type': 'string'},
        'description': {'type': 'string'},
        'type': {'enum': ['analog', 'digital']},
        'min': {'type': 'integer', 'default': 0},
        'center': {'type': 'integer', 'default': 127},
        'max': {'type': 'integer', 'default': 255},
    }
}

__schema__ = Controllable

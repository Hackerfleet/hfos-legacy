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

Profile = {
    'id': '#profile',
    'type': 'object',
    'name': 'Profile',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36, 'title': 'Unique User ID', 'description': 'HIDDEN'},
        "userdata": {
            "id": "#profile.userdata",
            "type": "object",
            "properties": {
                'name': {'type': 'string', 'minLength': 1, 'title': 'Name', 'description': 'First name'},
                'familyname': {'type': 'string', 'minLength': 1, 'title': 'Family Name',
                               'description': 'Last/Family name'},
                'nick': {'type': 'string', 'title': 'nickname', 'description': 'Nick/calling name'},
                'location': {'type': 'string', 'title': 'Current user location',
                             'description': 'Autoupdated (if possible) user location'},
                'd-o-b': {'type': 'string', 'title': 'Birthday', 'format': 'date', 'description': 'Date of birth'},
                'phone': {'type': 'string', 'title': 'Telephone number', 'description': 'International phone number'},
                'callsign': {'type': 'string', 'title': 'Radio callsign', 'description': 'HAM Radio etc callsign'},
                'shift': {'type': 'integer', 'title': 'Selected shift No.',
                          'description': '<a href="#/preferences/shifts">Setup shifts</a>'},
                'visa': {'type': 'boolean', 'title': 'Visas etc', 'description': 'Got all Visa documents etc?'},
                'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                          'description': 'Custom user notes'},
            }
        },
        "settings": {
            "id": "#profile.settings",
            "type": "object",
            "properties": {
                'color': {'type': 'string', 'title': 'User Color', 'format': 'color',
                          'description': 'Color used for map annotations, chat etc'},
                'theme': {'type': 'string', 'title': 'User Theme', 'description': 'Theme used for user interface'},
            }
        }
    }
}

__schema__ = Profile
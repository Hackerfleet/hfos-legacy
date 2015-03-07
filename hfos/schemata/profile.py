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

# {
#     'type': "object",
#     'name': 'Profile',
#     'properties': {
#         'name': {'type': "string", 'minLength': 2, 'title': "Name", 'description': "Name or alias"},
#         'title': {
#             'type': "string",
#             'enum': ['dr','jr','sir','mrs','mr','NaN','dj']
#         }
#     }
# }

Profile = {
    'type': 'object',
    'name': 'Profile',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36, 'title': 'Unique User ID', 'description': 'HIDDEN'},
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name', 'description': 'First name'},
        'familyname': {'type': 'string', 'minLength': 1, 'title': 'Family Name', 'description': 'Last/Family name'},
        'nick': {'type': 'string', 'title': 'nickname', 'description': 'Nick/calling name'},
        'location': {'type': 'string', 'title': 'Current user location',
                     'description': 'Autoupdated (if possible) user location'},
        'd-o-b': {'type': 'string', 'title': 'Birthday', 'format': 'date', 'description': 'Date of birth'},
        'phone': {'type': 'string', 'title': 'Telephone number', 'description': 'International phone number'},
        'callsign': {'type': 'string', 'title': 'Radio callsign', 'description': 'HAM Radio etc callsign'},
        'shift': {'type': 'integer', 'title': 'Selected shift No.',
                  'description': '<a href="#/preferences/shifts">Setup shifts</a>'},
        'color': {'type': 'string', 'title': 'User Color', 'format': 'color',
                  'description': 'Color used for map annotations, chat etc'},
        #'certs': {'type': 'array', 'items': 'string', 'title': '', 'description': ''},
        #'foodpref': {'type': 'string', 'title': '', 'description': ''},
        #'bunk': {'type': 'string', 'title': '', 'description': ''},
        'visa': {'type': 'boolean', 'title': 'Visas etc', 'description': 'Got all Visa documents etc?'},
        #'fees_paid': {'type': 'boolean', 'title': '', 'description': ''},
        #'fees_per_night': {'type': 'integer', 'title': '', 'description': ''},
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes', 'description': 'Custom user notes'}
    }
}

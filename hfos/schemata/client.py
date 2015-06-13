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
# 'type': "object",
# 'name': 'Profile',
# 'properties': {
# 'name': {'type': "string", 'minLength': 2, 'title': "Name", 'description': "Name or alias"},
#         'title': {
#             'type': "string",
#             'enum': ['dr','jr','sir','mrs','mr','NaN','dj']
#         }
#     }
# }

Profile = {
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
                        'title': 'Unique Client ID'
                        },
    }
}

__schema__ = Profile

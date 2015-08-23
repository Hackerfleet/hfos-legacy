"""
Schema: WikiPage
==============

Contains
--------

WikiPage: WikiPage to store collaborative data

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

WikiPage = {
    'id': '#wikipage',
    'type': 'object',
    'name': 'WikiPage',
    'properties': {
        'uuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique WikiPage ID'
        },
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name', 'description': 'Page name (url slug)'},
        'title': {'type': 'string', 'title': 'Page Title', 'description': 'Short title'},
        'text': {'type': 'string', 'format': 'html', 'title': 'Page content',
                 'description': 'Content'},
        'history': {'type': 'string'}
    }
}

__schema__ = WikiPage

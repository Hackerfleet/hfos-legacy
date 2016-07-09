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

from hfos.schemata.defaultform import defaultform

WikiPageSchema = {
    'id': '#wikipage',
    'type': 'object',
    'name': 'wikipage',
    'properties': {
        'uuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique WikiPage ID'
        },
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name', 'description': 'Page name (url slug)'},
        'title': {'type': 'string', 'title': 'Page Title', 'description': 'Short title'},
        'html': {'type': 'string', 'format': 'html', 'title': 'Page content',
                 'description': 'Content'},
        'text': {'type': 'string', 'title': 'Raw text', 'description': 'Unrendered raw text'},
        'history': {
            'type': 'array',
            'default': [],
            'items': {
                'type': 'string',
                'title': 'Snapshot content',
                'description': 'Snapshot data'
            }
        }
    }
}

WikiPageForm = defaultform

WikiPage = {'schema': WikiPageSchema, 'form': WikiPageForm}

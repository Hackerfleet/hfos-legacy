"""

Schema: Tag
============

Contains
--------

Systemwide Tag definition

See also
--------

Provisions

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""
from hfos.schemata.defaultform import savebutton

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

Tag = {
    'type': 'object',
    'id': '#tag',
    'name': 'tag',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36, 'title': 'Unique Tag ID',
                 'description': 'HIDDEN'},
        'name': {'type': 'string', 'title': 'Name',
                 'description': 'Name of Tag'},
        'creator': {'type': 'string', 'title': 'Creator',
                    'description': 'Creator of Tag'},
        'owneruuid': {'type': 'string', 'minLength': 36,
                      'title': "Owner's Unique ID", 'description': 'HIDDEN'},
        'color': {'type': 'string', 'format': 'color', 'title': 'Color of tag',
                  'description': 'Background color of tag'},
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                  'description': 'Descriptive Tag notes'},
        'references': {
            'type': 'array',
            'default': [],
            'items': {
                'type': 'object',
                'properties': {
                    'schema': {'type': 'string', 'minLength': 1,
                               'title': 'Schema reference',
                               'description': 'HIDDEN'},
                    'uuid': {'type': 'string', 'minLength': 36,
                             'title': 'Unique ID reference',
                             'description': 'HIDDEN'}
                }
            }
        }
    }
}

TagForm = [
    'name'
    'color'
    'notes',
    savebutton
]

Tag = {'schema': Tag, 'form': TagForm}

"""

Schema: Automat
===============

Contains
--------

Multiple automat-entry and a general automat schemata.

See also
--------

Provisions

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

Incident = {

}

AutomatSchema = {
    'type': 'object',
    'id': '#automat',
    'name': 'automat',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36,
                 'title': 'Unique Automat Event ID', 'description': 'HIDDEN'},
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
                 'description': 'Name of automat entry'},
        'severity': {'type': 'string', 'enum': ['Info', 'Warning', 'Critical'],
                     'default': 'Info'},
        'owner': {'type': 'string', 'minLength': 36,
                      'title': "Owner's Unique ID", 'description': 'HIDDEN'},
        'time': {'type': 'string', 'format': 'datetimepicker',
                 'title': 'Event time',
                 'description': 'Date and time of event'},
        'category': {'type': 'string', 'title': 'Category',
                     'enum': ['Incident', 'Navigation', 'Technical', 'Bridge'],
                     'description': 'Category of log event'},
        'subcategory'
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                  'description': 'Entry notes'},

    }
}

Automat = {'schema': AutomatSchema, 'form': {}}

"""

Schema: Logbook
===============

Contains
--------

Multiple logbook-entry and a general logbook schemata.

See also
--------

Provisions

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

Incident = {

}

LogbookSchema = {
    'type': 'object',
    'id': '#logbook',
    'name': 'logbook',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36,
                 'title': 'Unique Logbook Event ID', 'description': 'HIDDEN'},
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
                 'description': 'Name of logbook entry'},
        'severity': {'type': 'string', 'enum': ['Info', 'Warning', 'Critical'],
                     'default': 'Info'},
        'owneruuid': {'type': 'string', 'minLength': 36,
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

Logbook = {'schema': LogbookSchema, 'form': {}}

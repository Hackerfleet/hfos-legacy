"""
Schema: Radio
==============

Contains
--------

Radio: Radio configurations to store onboard radio system data

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = 'riot'

RadioConfig = {
    'id': '#radio',
    'type': 'object',
    'name': 'radio',
    'properties': {
        'uuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                 'type': 'string',
                 'title': 'Unique Radio ID'
                 },
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name', 'description': 'Radio name'},
        'model': {'type': 'string', 'minLength': 1, 'title': 'Model', 'description': 'Radio model'},
        'manufacturer': {'type': 'string', 'minLength': 1, 'title': 'Manufacturer',
                         'description': 'Radio manufacturer'},
        'radiotype': {'type': 'string', 'title': 'Type', 'description': 'Type of radio'},
        'color': {'type': 'string', 'title': 'Radio Color', 'format': 'color',
                  'description': 'Color used for map annotations etc'},
        'tx-power': {'type': 'number', 'title': 'Radio transmission power',
                     'description': 'Maximum Radio transmission power'},
        'tx-height': {'type': 'number', 'title': 'Radio transmitting antenna height',
                      'description': 'Antenna mount height above water surface'},
        'tx-freq': {'type': 'number', 'title': 'Frequency',
                    'description': 'Default operating frequency'},
        'notes': {'type': 'string', 'format': 'html', 'title': 'Radio notes',
                  'description': 'Custom radio notes'},

    }
}

RadioForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'name', 'color', 'manufacturer', 'model'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'tx-power', 'tx-freq', 'tx-height'
                ]
            }
        ]
    },
    'notes',
    {
        'type': 'submit',
        'title': 'Save radio',
    }
]

__form__ = RadioForm
__schema__ = RadioConfig

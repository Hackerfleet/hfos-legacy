"""
Schema: Radio
==============

Contains
--------

Radio: Radio configurations to store onboard radio system data

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import editbuttons
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

RadioConfigSchema = base_object('radio')

RadioConfigSchema['properties'].update({
    'model': {'type': 'string', 'minLength': 1, 'title': 'Model',
              'description': 'Radio model'},
    'manufacturer': {'type': 'string', 'minLength': 1,
                     'title': 'Manufacturer',
                     'description': 'Radio manufacturer'},
    'radiotype': {'type': 'string', 'title': 'Type',
                  'description': 'Type of radio'},
    'color': {'type': 'string', 'title': 'Radio Color', 'format': 'color',
              'description': 'Color used for map annotations etc'},
    'tx-power': {'type': 'number', 'title': 'Radio transmission power',
                 'description': 'Maximum Radio transmission power'},
    'tx-height': {'type': 'number',
                  'title': 'Radio transmitting antenna height',
                  'description': 'Antenna mount height above water '
                                 'surface'},
    'tx-freq': {'type': 'number', 'title': 'Frequency',
                'description': 'Default operating frequency'},
    'notes': {'type': 'string', 'format': 'html', 'title': 'Radio notes',
              'description': 'Custom radio notes'},

})

RadioConfigForm = [
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
    editbuttons
]

RadioConfig = {'schema': RadioConfigSchema, 'form': RadioConfigForm}

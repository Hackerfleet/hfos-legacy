"""
Schema: SensorData
====================

Contains
--------

SensorData:

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

SensorDataSchema = {
    'id': '#sensorData',
    'title': 'SensorData',
    'type': 'object',
    'name': 'sensordata',
    'properties': {
        'value': {'title': 'Value', 'description':
            'Sensordata Value'},
        'timestamp': {'type': 'number', 'title': 'Timestamp',
                      'description': 'Log Message timestamp (\xc2Sec)'},
        'type': {'type': 'string'}
    }
}

SensorDataForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [

                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [

                ]
            }
        ]
    },
    'description'
]

SensorData = {'schema': SensorDataSchema, 'form': SensorDataForm}

"""
Schema: SensorData
====================

Contains
--------

SensorData:

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

SensorDataSchema = base_object('sensorData', has_owner=False, has_uuid=False)

SensorDataSchema['properties'].update({
    'value': {
        'title': 'Value', 'description': 'Sensordata Value'
    },
    'timestamp': {
        'type': 'number', 'title': 'Timestamp',
        'description': 'Log Message timestamp (microSec)'
    },
    'type': {
        'type': 'string'
    }
})

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

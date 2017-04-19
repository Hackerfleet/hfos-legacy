"""
Schema: SensorDataType
======================

Contains
--------

SensorDataType

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import savebutton
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

SensorDataTypeSchema = base_object('sensordatatype', has_owner=False)

SensorDataTypeSchema['properties'].update({
    'sentence': {'type': 'string', 'title': 'Sentence',
                 'description': '(At least for) NMEA Sentence Type'},
    'title': {'type': 'string', 'title': 'Title',
              'description': 'Descriptive Title'},
    'description': {'type': 'string', 'title': 'Description',
                    'description': 'Sensor Type Description'},
    'type': {'type': 'string', 'title': 'Type',
             'description': 'Sensor Data Value Type'},
    'timestamp': {'type': 'number', 'title': 'Timestamp',
                  'description': 'Date of last known Sensor Value'},
    'lastvalue': {'type': 'string', 'title': 'Last Value',
                  'description': 'Last known Sensor Value'},
    'record': {'type': 'boolean', 'title': 'Record Sensor',
               'description': 'Record value changes of this sensor.'},
    'bus': {'type': 'string', 'title': 'Connected Bus',
            'description': 'Name of bus, the device is connected on.'}
})

SensorDataTypeForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'sentence', 'title', 'name', 'lastvalue'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'bus', 'record', 'timestamp', 'type'
                ]
            }
        ]
    },
    'description',
    savebutton
]

SensorDataType = {'schema': SensorDataTypeSchema, 'form':
    SensorDataTypeForm}

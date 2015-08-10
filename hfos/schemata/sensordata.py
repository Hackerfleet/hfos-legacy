"""
Schema: SensorData
====================

Contains
--------

SensorData:

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

SensorData = {
    'id': '#SensorData',
    'type': 'object',
    'name': 'SensorData',
    'properties': {
        'uuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                 'type': 'string',
                 'title': 'Unique SensorData ID'
                 },
        'Time_Created': {'title': 'Creation time', 'type': 'number', 'description': 'When this event was logged'},
        'Depth_BelowTransducer': {'title': 'Depth.BelowTransducer', 'type': 'number',
                                  'description': 'Depth.BelowTransducer'},
        'Depth_Water': {'title': 'Depth.Water', 'type': 'number', 'description': 'Depth.Water'},
        'GPS_Quality': {'title': 'GPS Fix Quality', 'type': 'number', 'description': 'GPS.Fix'},
        'GPS_LatLon': {'title': 'GPS.LatLon', 'type': 'string', 'description': 'GPS.LatLon'},
        'GPS_SatCount': {'title': 'GPS.SatCount', 'type': 'number', 'description': 'GPS.SatCount'},
        'Heading': {'title': 'Heading', 'type': 'number', 'description': 'Heading'},
        'Heading_Magnetic_Deviation': {'title': 'Heading.Magnetic.Deviation', 'type': 'number',
                                       'description': 'Heading.Magnetic.Deviation'},
        'Heading_Magnetic_Sensor': {'title': 'Heading.Magnetic.Sensor', 'type': 'number',
                                    'description': 'Heading.Magnetic.Sensor'},
        'Heading_Magnetic_Variation': {'title': 'Heading.Magnetic.Variation', 'type': 'number',
                                       'description': 'Heading.Magnetic.Variation'},
        'Heading_Magnetic': {'title': 'Heading.Magnetic', 'type': 'number', 'description': 'Heading.Magnetic'},
        'Heading_True': {'title': 'Heading.True', 'type': 'number', 'description': 'Heading.True'},
        'Water_Temperature': {'title': 'Water.Temperature', 'type': 'number', 'description': 'Water.Temperature'},

        'Rudder_Angle': {'title': 'Rudder.Angle', 'type': 'number', 'description': 'Rudder.Angle'},
        'Track_Water_Degrees': {'title': 'Track.Water.Degrees', 'type': 'number', 'description': 'Track.Water.Degrees'},
        'Track_Water_Speed': {'title': 'Track.Water.Speed', 'type': 'number', 'description': 'Track.Water.Speed'},
        'Track_True_Degrees': {'title': 'Track.True.Degrees', 'type': 'number', 'description': 'Track.True.Degrees'},
        'Track_True_Speed': {'title': 'Track.True.Speed', 'type': 'number', 'description': 'Track.True.Speed'},
        'Time_UTC': {'title': 'Time.UTC', 'type': 'number', 'description': 'Time.UTC'},
        'Wind_Speed_True': {'title': 'Wind.Speed.True', 'type': 'number', 'description': 'Wind.Speed.True'},
        'Wind_Direction_True': {'title': 'Wind.Direction.True', 'type': 'number', 'description': 'Wind.Direction.True'},
        'Wind_Direction_LeftRight': {'title': 'Wind.Direction.LeftRight', 'type': 'number',
                                     'description': 'Wind.Direction.LeftRight'},
        'Wind_Direction_Relative': {'title': 'Wind.Direction.Relative', 'type': 'number',
                                    'description': 'Wind.Direction.Relative'},
        'Wind_Speed_Relative': {'title': 'Wind.Speed.Relative', 'type': 'number', 'description': 'Wind.Speed.Relative'}
    }
}

SensorValueTypes = []
for key in SensorData['properties']:
    if key not in ('uuid', 'Time_Created'):
        SensorValueTypes.append(key)

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
    'description',
    {
        'type': 'submit',
        'title': 'Save Sensor Data configuration',
    }
]

__schema__ = SensorData
__form__ = SensorDataForm

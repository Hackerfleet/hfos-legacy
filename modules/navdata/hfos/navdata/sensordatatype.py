#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2018 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""
Schema: SensorDataType
======================

Contains
--------

SensorDataType


"""

from hfos.schemata.defaultform import savebutton
from hfos.schemata.base import base_object

SensorDataTypeSchema = base_object('sensordatatype',
                                   has_owner=False,
                                   all_roles='crew')

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

SensorDataType = {
    'schema': SensorDataTypeSchema,
    'form': SensorDataTypeForm
}

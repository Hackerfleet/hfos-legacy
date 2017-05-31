#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2017 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "GPLv3"

"""
Schema: Radio
==============

Contains
--------

Radio: Radio configurations to store onboard radio system data


"""

from hfos.schemata.defaultform import editbuttons
from hfos.schemata.base import base_object

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

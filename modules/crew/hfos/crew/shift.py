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
Schema: Shift
=============

Contains
--------

Shift: Stores shift information for timetables and assisted rotation


"""

from hfos.schemata.defaultform import *
from hfos.schemata.base import uuid_object

# TODO: Convert to base_object

ShiftSchema = {
    'id': '#shiftconfig',
    'type': 'object',
    'name': 'shiftconfig',
    'properties': {
        'uuid': uuid_object('Unique Shift ID'),
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
                 'description': 'Shift name'},
        'locked': {'type': 'boolean', 'title': 'Locked Shift',
                   'description': 'Determines whether the Shift should '
                                  'be locked against changes.'},
        'description': {'type': 'string', 'format': 'html',
                        'title': 'Shift description',
                        'description': 'Shift description'},
        'useruuid': uuid_object('Associated Unique User ID')
    },
    "required": [
        'uuid'
    ]
}

ShiftForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'name'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'shared', 'locked'
                ]
            },
        ]
    },
    'description',
    editbuttons
]

ShiftConfig = {'schema': ShiftSchema, 'form': ShiftForm}

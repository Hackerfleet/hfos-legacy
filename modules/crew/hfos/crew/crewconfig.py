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
Schema: Crewconfig
==================

Contains
--------

crewconfig: Structure to store information about crews, for timetable and
other useful features


"""

from hfos.schemata.defaultform import *
from hfos.schemata.base import base_object

CrewSchema = base_object('crewconfig')

CrewSchema['properties'].update({
    'locked': {'type': 'boolean', 'title': 'Locked Crew',
               'description': 'Determines whether the Crew should '
                              'be locked against changes.'},
    'shared': {'type': 'boolean', 'title': 'Shared Crew',
               'description': 'Share Crew with the crew'},
    'description': {'type': 'string', 'format': 'html',
                    'title': 'Crew description',
                    'description': 'Crew description'},
})

CrewForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'name',
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

CrewConfig = {'schema': CrewSchema, 'form': CrewForm}

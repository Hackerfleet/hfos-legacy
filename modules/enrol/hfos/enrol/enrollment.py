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
Schema: Enrollmentconfig
==================

Contains
--------

enrollmentconfig: Structure to store information about enrollments,
for timetable and
other useful features


"""

from hfos.schemata.defaultform import *
from hfos.schemata.base import base_object

EnrollmentSchema = base_object('enrollment')

EnrollmentSchema['properties'].update({
    'mail-address': {'type': 'string', 'title': 'Address',
                     'description': 'Enrollment email address'},
    'description': {'type': 'string', 'format': 'html',
                    'title': 'Enrollment description',
                    'description': 'Enrollment description'},
})

EnrollmentForm = [
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
                    'mail-address'
                ]
            },
        ]
    },
    'description',
    editbuttons
]

Enrollment = {'schema': EnrollmentSchema, 'form': EnrollmentForm}

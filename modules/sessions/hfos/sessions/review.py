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
Schema: Review
===============

Contains
--------

Review: Generic object to store data about lectures, lightning talks etc. 


"""

from hfos.schemata.defaultform import editbuttons, section, lookup_field, rating_widget
from hfos.schemata.base import base_object, uuid_object

ReviewSchema = base_object('review', roles_create='chair', hide_owner=False)

ReviewSchema['properties'].update({
    'status': {
        'type': 'string',
        'enum': [
            'Denied',
            'Accepted',
            'Not reviewed'
        ],
        'default': 'Not reviewed'
    },
    'calendar_reference': uuid_object(title='Calendar'),
    'session_reference': uuid_object(title='Session'),
    'comments': {'type': 'string', 'format': 'html'},
    'rating': {'type': 'integer'}
})

ReviewForm = [
    section(2, 2, [
        [
            'owner', 'status'
        ],
        [
            lookup_field('calendar_reference', 'calendar'),
            lookup_field('session_reference', 'session')
        ]
    ]),
    rating_widget(),
    'comments',
    editbuttons
]

Review = {'schema': ReviewSchema, 'form': ReviewForm}

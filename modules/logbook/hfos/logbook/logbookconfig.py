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
Schema: Logbookconfig
=====================

Contains
--------

Logbook: Structure to store logbook configurations


"""

from hfos.schemata.defaultform import *
from hfos.schemata.base import base_object

LogbookSchema = base_object('logbookconfig', all_roles='crew')

LogbookSchema['properties'].update({
    'locked': {
        'type': 'boolean', 'title': 'Locked Logbook',
        'description': 'Determines whether the Logbook should '
                       'be locked against changes.'
    },
    'shared': {
        'type': 'boolean', 'title': 'Shared Logbook',
        'description': 'Share Logbook with the crew'
    },
    'description': {
        'type': 'string', 'format': 'html',
        'title': 'Logbook description',
        'description': 'Logbook description'
    }
})

LogbookForm = [
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

LogbookConfig = {'schema': LogbookSchema, 'form': LogbookForm}

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
Schema: SessionType
===============

Contains
--------

SessionType: Generic object to store data about lectures, lightning talks etc. 


"""

from hfos.schemata.defaultform import editbuttons, section
from hfos.schemata.base import base_object

SessionTypeSchema = base_object('sessiontype',
                                roles_write=['chair'],
                                roles_create=['chair'],
                                roles_read= ['crew'],
                                roles_list=['crew'])

SessionTypeSchema['properties'].update({
    'name': {'type': 'string', 'title': 'Title',
             'description': 'Title of SessionType'},
    'open': {'type': 'boolean', 'title': 'Open', 'description': 'Allow SessionType type registration'},
    'length': {'type': 'number', 'title': 'Length', 'description': 'Duration of SessionType in minutes'},
})

SessionTypeForm = [
    'name',
    section(1, 2, [['open', 'length']]),
    editbuttons
]

SessionType = {'schema': SessionTypeSchema, 'form': SessionTypeForm}

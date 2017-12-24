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

Schema: User
============

Account credentials and administrativa

Contains
--------

User: Useraccount object


"""
from hfos.schemata.defaultform import noform
from hfos.schemata.base import base_object

UserSchema = base_object('user', roles_list=['crew'])

UserSchema['properties'].update({
    'passhash': {
        'type': 'string'
    },
    'roles': {
        'type': 'array',
        'items': {
            'type': 'string'
        },
        'default': ['crew']
    },
    'needs_password_change': {
        'type': 'boolean',
        'default': True,
    }
})

UserOptions = {
    'hidden': ['passhash', 'roles', 'needs_password_change']
}

User = {'schema': UserSchema, 'form': noform, 'options': UserOptions}

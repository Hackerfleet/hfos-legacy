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

Schema: Node State
====================

Node state objects

Contains
--------

NodeState: Nodestate object


"""

from hfos.schemata.defaultform import lookup_field, editbuttons
from hfos.schemata.base import base_object, uuid_object

NodeStateSchema = base_object('nodestate',
                              roles_write='admin',
                              roles_create='admin',
                              roles_list='crew',
                              roles_read='crew')

NodeStateSchema['properties'].update({
    'color': {
        'type': 'string',
        'format': 'color'
    },
    'readonly': {
        'type': 'boolean',
        'default': False,
        'description': 'Not user-toggleable when checked'
    },
    'excluded': {
        'type': 'array',
        'default': [],
        'items': uuid_object('Excluded')
    },
    'label-activated': {
        'type': 'string'
    },
    'icon': {
        'type': 'string'
    },
    'active': {
        'type': 'boolean',
        'default': False
    },
    'group': {
        'type': 'string'
    },
    'untrigger': {
        'type': 'array',
        'default': [],
        'items': uuid_object('Untrigger')
    },
    'position': {
        'type': 'object',
        'properties': {
            'x': {'type': 'number'},
            'y': {'type': 'number'}
        }
    },
    'size': {
        'type': 'object',
        'properties': {
            'width': {'type': 'number', 'default': 2},
            'height': {'type': 'number', 'default': 2}
        }
    }
})

NodeStateForm = [
    'name',
    'icon',
    'color',
    'active',
    'label-activated',
    'readonly',
    'group',
    {
        'key': 'excluded',
        'validationMessage': ' ',
        'disableErrorState': True,
        'items': [
            lookup_field('excluded[]', 'nodestate'),
        ]
    },
    {
        'key': 'untrigger',
        'validationMessage': ' ',
        'disableErrorState': True,
        'items': [
            lookup_field('untrigger[]', 'nodestate')
        ]
    },
    editbuttons
]

NodeStateOptions = {
}

NodeState = {
    'schema': NodeStateSchema,
    'form': NodeStateForm,
    'options': NodeStateOptions
}

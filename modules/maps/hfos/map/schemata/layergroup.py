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

Schema: LayerGroup
==================

Contains
--------

LayerGroup: A configurable group of predefined layers

See also
--------

Provisions


"""

from hfos.schemata.defaultform import editbuttons
from hfos.schemata.base import base_object, uuid_object

LayerGroupSchema = base_object('layergroup',
                               roles_read=['admin', 'crew'],
                               roles_write=['admin', 'navigator'],
                               roles_create=['admin', 'navigator'],
                               roles_list=['admin', 'crew']
                               )

LayerGroupSchema['properties'].update({
    'owner': {'type': 'string', 'minLength': 36,
              'title': "Owner's Unique ID", 'description': 'HIDDEN'},
    'color': {'type': 'string', 'title': 'Group Color', 'format': 'color',
              'description': 'This group''s color indicator'},
    'shared': {'type': 'boolean', 'title': 'Shared group',
               'description': 'Share group with the crew'},
    'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
              'description': 'Custom user notes'},
    'layers': {
        'type': 'array',
        'items': uuid_object('Unique Layer ID')
    }
})

LayerGroupForm = [
    'name',
    'notes',
    {
        'key': 'layers',
        'add': "Add layer",
        'style': {
            'add': "btn-success"
        },
        'items': [
            {
                'key': 'layers[]',
                'type': 'strapselect',
                'placeholder': 'Select a Layer',
                'options': {
                    "type": "layer",
                    "asyncCallback": "$ctrl.getFormData",
                    "map": {'valueProperty': "uuid", 'nameProperty': 'name'}
                }
            }
        ]
    },
    editbuttons
]

LayerGroup = {'schema': LayerGroupSchema, 'form': LayerGroupForm}

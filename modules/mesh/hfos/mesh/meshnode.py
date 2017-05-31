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

Schema: MeshNode
============

Contains
--------

MeshNode reference entry for the mesh to set up pump start times and
durations as well as conditions..


"""

from hfos.schemata.defaultform import savebutton
from hfos.schemata.base import base_object

MeshNodeSchema = base_object('meshnode')

MeshNodeSchema['properties'].update({
    'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
              'description': 'Entry notes'},
    'hub': {'type': 'boolean', 'title': 'Hub node',
            'description': 'This node has data about other nodes'},
    'address': {
        'type': 'string',
        'format': 'ip-address',
        'title': 'IP Address',
        'description': 'Last known IP address of node'
    },
    'last': {
        'type': 'string', 'format': 'datetimepicker',
        'title': 'Last Seen',
        'description': 'Last date and time, this node has been seen online'
    }
})

MeshNodeForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'name', 'address'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'last'
                ]
            },
        ]
    },
    'notes',
    {
        'key': 'Toggle',
        'type': 'button',
        'onClick': 'formAction("hfos.mesh.zmqmesh", "toggle", model.uuid)',
        'title': 'Toggle MeshNode'
    },
    savebutton
]

MeshNode = {'schema': MeshNodeSchema, 'form': MeshNodeForm}

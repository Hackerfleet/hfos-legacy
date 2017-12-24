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

Schema: Mapview
===============

Contains
--------

MapView: User generated Mapviews


"""
from hfos.schemata.defaultform import lookup_field, editbuttons
from hfos.schemata.base import base_object, uuid_object

MapViewSchema = base_object('mapview',
                            roles_read=['crew'],
                            roles_write=['navigator', 'crew'],
                            roles_create=['navigator', 'crew'],
                            roles_list=['crew']
                            )

MapViewSchema['properties'].update({
    'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
             'description': 'Name of view'},
    'color': {'type': 'string', 'title': 'View Color', 'format': 'color',
              'description': 'This views color indicator'},
    'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
              'description': 'Custom user notes'},
    'viewtype': {'enum': ['vessel', 'user'], 'title': 'View Type',
                 'description': 'Shows what type of mapview this is'},
    'layergroups': {
        'type': 'array',
        'description': 'List of available Layergroups',
        'items': uuid_object('Select a Layergroup'),
        'default': []
    },
    'coords': {
        # TODO: Decide if we want to integrate null island as default
        "lat": {
            "id": "lat",
            "type": "number",
            "maximum": 90,
            "minimum": -90,
            "title": "Latitude of coordinate.",
            "description": "",
            "name": "lat",
            "default": 54.17805
        },
        "lng": {
            "id": "lng",
            "type": "number",
            "maximum": -180,
            "minimum": 180,
            "title": "Longitude of coordinate.",
            "description": "",
            "name": "lon",
            "default": 7.88669
        },
        "zoom": {
            "id": "zoom",
            "type": "integer",
            "multipleOf": 1,
            "maximum": 20,
            "minimum": 1,
            "title": "Zoom of view.",
            "description": "",
            "name": "zoom",
            "default": 16
        },
        "autoDiscover": {
            "id": "autoDiscover",
            "type": "boolean",
            "title": "Autodiscover on device.",
            "description": "",
            "name": "autoDiscover",
            "default": True
        }

    }
})

MapViewForm = [
    'name',
    'color',
    'notes',
    {
        'key': 'layergroups',
        'validationMessage': ' ',
        'disableErrorState': True,
        'items': [
            lookup_field('layergroups[]', 'layergroup'),
        ]
    },
    editbuttons
]

MapView = {'schema': MapViewSchema, 'form': MapViewForm}

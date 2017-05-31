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

Schema: Coords
==============

Contains
--------

MapCoords: Leaflet compatible lat/lon/zoom combination


"""

MapCoordsSchema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "id": "mapcoords",
    "type": "object",
    "additionalProperties": True,
    "title": "Root schema.",
    "description": "An explanation about the puropose of this instance "
                   "described by this schema.",
    "name": "mapcoords",
    "properties": {
        "lat": {
            "id": "lat",
            "type": "number",
            "maximum": 90,
            "minimum": -90,
            "title": "Latitude of coordinate.",
            "description": "",
            "name": "lat"
        },
        "lon": {
            "id": "lon",
            "type": "number",
            "maximum": -180,
            "minimum": 180,
            "title": "Longitude of coordinate.",
            "description": "",
            "name": "lon"
        },
        "zoom": {
            "id": "zoom",
            "type": "integer",
            "multipleOf": 1,
            "maximum": 20,
            "minimum": 1,
            "title": "Zoom of view.",
            "description": "",
            "name": "zoom"
        }
    },
    "required": [
        "lat",
        "lon",
        "zoom"
    ]
}

MapCoords = {'schema': MapCoordsSchema, 'form': {}}

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

Schema: Geometry
================

This is non-model schema for integration into other schemata.

Contains
--------

geometry: Any valid GeoJSON geometry (Points, Multipoints, Linestrings, Multilinestrings, Polygons and Multipolygons)


"""
from hfos.schemata.defaultform import noform

GeometrySchema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "id": "http://json-schema.org/geojson/geometry.json#",
    "title": "geometry",
    "description": "One geometry as defined by GeoJSON",
    "type": "object",
    "required": ["type", "coordinates"],
    "oneOf": [
        {
            "title": "Point",
            "properties": {
                "type": {"enum": ["Point"]},
                "coordinates": {"$ref": "#/definitions/position"}
            }
        },
        {
            "title": "MultiPoint",
            "properties": {
                "type": {"enum": ["MultiPoint"]},
                "coordinates": {"$ref": "#/definitions/positionArray"}
            }
        },
        {
            "title": "LineString",
            "properties": {
                "type": {"enum": ["LineString"]},
                "coordinates": {"$ref": "#/definitions/lineString"}
            }
        },
        {
            "title": "MultiLineString",
            "properties": {
                "type": {"enum": ["MultiLineString"]},
                "coordinates": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/lineString"}
                }
            }
        },
        {
            "title": "Polygon",
            "properties": {
                "type": {"enum": ["Polygon"]},
                "coordinates": {"$ref": "#/definitions/polygon"}
            }
        },
        {
            "title": "MultiPolygon",
            "properties": {
                "type": {"enum": ["MultiPolygon"]},
                "coordinates": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/polygon"}
                }
            }
        }
    ],
    "definitions": {
        "position": {
            "description": "A single position",
            "type": "array",
            "minItems": 2,
            "items": [{"type": "number"}, {"type": "number"}],
            "additionalItems": False
        },
        "positionArray": {
            "description": "An array of positions",
            "type": "array",
            "items": {"$ref": "#/definitions/position"}
        },
        "lineString": {
            "description": "An array of two or more positions",
            "allOf": [
                {"$ref": "#/definitions/positionArray"},
                {"minItems": 2}
            ]
        },
        "linearRing": {
            "description": "An array of four positions where the first equals the last",
            "allOf": [
                {"$ref": "#/definitions/positionArray"},
                {"minItems": 4}
            ]
        },
        "polygon": {
            "description": "An array of linear rings",
            "type": "array",
            "items": {"$ref": "#/definitions/linearRing"}
        }
    }
}

GeometryForm = noform

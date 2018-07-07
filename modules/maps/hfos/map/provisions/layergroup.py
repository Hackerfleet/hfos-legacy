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

Provisioning: Layergroups
=========================

Contains
--------

Predefined groups of layers.


"""

layergroups = [
    {
        "name": "Default",
        "uuid": "076b0b52-9ac8-4fdc-9e39-11141807e0e8",
        "shared": True,
        "notes": "Open Street Map and Open Sea Map, Satellite Overlay",
        "layers": [
            '2837298e-a3e8-4a2e-8df2-f475554d2f23',  # OSM
            '2bedb0d2-be9f-479c-9516-256cd5a0baae',  # OpenSeaMap
            '72611470-39b3-4982-8991-2ad467b06fc9'  # ESRI Satellite Shade Ovl
        ]
    }, {
        "name": "GDAL Charts",
        "uuid": "6a18fdad-93a2-4563-bb8a-cb5888f43300",
        "shared": True,
        "notes": "Imported GDAL charts",
        "layers": [
            '2837298e-a3e8-4a2e-8df2-f475554d2f23',  # OSM
            '2bedb0d2-be9f-479c-9516-256cd5a0baae',  # OpenSeaMap
            '72611470-39b3-4982-8991-2ad467b06fc9'  # ESRI Satellite Shade Ovl
        ]
    }, {
        "name": "Satellite",
        "uuid": "889f580f-0aa4-46b6-96a1-87ef19030b0b",
        "shared": True,
        "notes": "ESRI Satellite and Open Sea Map",
        "layers": [
            '582d2ef3-759e-49f7-81ab-8dbe224d618a',
            # ESRI Satellite World Imagery Base
            '19e5704e-68a2-435e-9f21-ac389973cc7a',
            # ESRI Satellite Hill Shade Base
            '3a4cceaa-3e8b-4f65-85ee-2ff9f6de6a71',  # Openstreetmap Overlay
            '2bedb0d2-be9f-479c-9516-256cd5a0baae',  # OpenSeaMap Overlay
        ]
    }, {
        "name": "Weather",
        "uuid": "22d57d5b-ceb2-47b3-9831-06290e6cbfe7",
        "shared": True,
        "notes": "Open Street Map, Open Sea Map + OpenWeatherMaps",
        "layers": [
            '2837298e-a3e8-4a2e-8df2-f475554d2f23',  # OSM
            '2bedb0d2-be9f-479c-9516-256cd5a0baae',  # OpenSeaMap
            '7b73024e-9ede-4c90-821d-9c24c0cc0ff6',  # OWM Cloudlayer Ovl
        ]
    }
]


provision = {'data': layergroups, 'model': 'layergroup'}

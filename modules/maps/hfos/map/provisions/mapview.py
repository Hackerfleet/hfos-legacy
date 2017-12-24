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

Provisioning: Mapview
=====================

Contains
--------

Mapview skeleton for ships


"""

from hfos.provisions.base import provisionList
from hfos.database import objectmodels
from hfos.logger import hfoslog

Mapviews = [
    {
        'name': 'Default OpenSeaMap + OpenStreetMap',
        'uuid': 'b69104cf-8ee7-4c81-aeca-dde272d67b63',
        'notes': 'Default empty mapview.',
        'layergroups': [
            '076b0b52-9ac8-4fdc-9e39-11141807e0e8',
            '22d57d5b-ceb2-47b3-9831-06290e6cbfe7'
        ]
    },
]


def provision(**kwargs):
    provisionList(Mapviews, objectmodels['mapview'],
                  indices=['name'], indices_types=['text'], indices_unique=[False],
                  **kwargs)
    hfoslog('Provisioning: Mapviews: Done.', emitter='PROVISIONS')


if __name__ == "__main__":
    provision()

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

Schema: Route
=============

Contains
--------

Route: A configurable group of predefined layers

See also
--------

Provisions


"""

from hfos.schemata.defaultform import editbuttons
from hfos.schemata.base import base_object

RouteSchema = base_object('route',
                          roles_read=['admin', 'crew'],
                          roles_write=['admin', 'navigator'],
                          roles_create=['admin', 'navigator'],
                          roles_list=['admin', 'crew']
                          )

RouteSchema['properties'].update({
    'color': {'type': 'string', 'title': 'Group Color', 'format': 'color',
              'description': 'This group''s color indicator'},
    'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
              'description': 'Custom user notes'},
    'etd': {
        'type': 'integer',
        'format': 'datetimepicker',
        'title': 'ETD',
        'description': 'Estimated Time of Departure'
    },
    'eta': {
        'type': 'integer',
        'format': 'datetimepicker',
        'title': 'ETA',
        'description': 'Estimated Time of Arrival'
    },
    'origin_port': {
        'type': 'string',
        'title': 'Origin',
        'description': 'Origin Port'
    },
    'destination_port': {
        'type': 'string',
        'title': 'Destination',
        'description': 'Destination Port'
    },
    'ettt': {
        'type': 'integer',
        'format': 'datetimepicker',
        'title': 'ETTT',
        'description': 'estimated total travel time',
        'readonly': True,
    },
    'attt': {
        'type': 'integer',
        'format': 'datetimepicker',
        'title': 'ATTT',
        'description': 'actual total travel time',
        'readonly': True,
    },
    'atd': {
        'type': 'integer',
        'format': 'datetimepicker',
        'title': 'ATD',
        'description': 'actual time of departure',
        'readonly': True,
    },
    'ata': {
        'type': 'integer',
        'format': 'datetimepicker',
        'title': 'ATA',
        'description': 'Actual time of arrival',
        'readonly': True,
    },
    'distance': {
        'type': 'integer',
        'title': 'Distance',
        'description': 'Distance of route',
        'readonly': True,
    }
})

RouteForm = [
    '*',
    editbuttons
]

Route = {'schema': RouteSchema, 'form': RouteForm}

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

Schema: Geoobject
=================

Contains
--------

Geoobject: General geoobject configuration data encapsulating geojson

See also
--------

Provisions


"""

from hfos.schemata.defaultform import defaultform
from hfos.schemata.base import base_object

GeoObjectSchema = base_object('geoobject', all_roles='crew')

GeoObjectSchema['properties'].update({
    'layer': {
        'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                   'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
        'type': 'string',
        'title': 'Unique GeoObject Layer ID'
    },
    'iconcolor': {'type': 'string', 'title': 'Icon Color',
                  # 'format': 'color',
                  'description': 'GeoObject icon color indicator', 'default':
                      'white'},
    'newvar': {'type': 'string', 'title': 'Foobar'},
    'icon': {'type': 'number', 'title': 'Icon',
             'description': 'Custom user icon', 'default': 'flag'},
    'shared': {'type': 'boolean', 'title': 'Shared GeoObject',
               'description': 'Share GeoObject with the crew'},
    'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
              'description': 'Custom user notes'},
    'minZoom': {'type': 'number', 'description': 'Minimum zoom number.',
                'default': 0},
    'maxZoom': {'type': 'number', 'description': 'Maximum zoom number.',
                'default': 18},
    'opacity': {'type': 'number',
                'description': 'The opacity of the GeoObject.',
                'default': 1.0},
    'zIndexFoo': {'type': 'number',
                  'description': 'The explicit zIndex of the GeoObject.'
                                 'Not set by default.',
                  },

    'geojson': {
        'type': 'object',
        'default': {},
        'properties': {
            'newsub': {'type': 'string'}
        }
    }
}
)
GeoObject = {'schema': GeoObjectSchema, 'form': defaultform}

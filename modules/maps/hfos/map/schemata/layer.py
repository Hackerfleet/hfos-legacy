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

Schema: Layer
=============

Contains
--------

Layer: General and renderer specific layer configuration data.

See also
--------

Provisions


"""

from hfos.schemata.defaultform import defaultform
from hfos.schemata.base import base_object

LayerSchema = base_object('layer',
                          roles_read=['crew'],
                          roles_write=['navigator'],
                          roles_create=['navigator'],
                          roles_list=['crew']
                          )

LayerSchema['properties'].update({
    'color': {
        'type': 'string', 'title': 'View Color', 'format': 'color',
        'description': 'This views color indicator'
    },
    'notes': {
        'type': 'string', 'format': 'html', 'title': 'User notes',
        'description': 'Custom user notes'
    },
    'cached': {
        'type': 'boolean', 'title': 'Use tilecache',
        'description': 'Cache all downloaded map data'
    },
    'baselayer': {
        'type': 'boolean', 'title': 'Can be baselayer',
        'description': 'Baselayer (can be the first layer of a '
                       'group)'
    },
    'cachesize': {
        'type': 'number',
        'description': 'Current size of cache.'
    },
    'url': {
        'type': 'string', 'format': 'html', 'title': 'User notes',
        'description': 'Layer URL'
    },
    'path': {
        'type': 'string', 'title': 'Filesystem location of layer',
        'description': 'HIDDEN'
    },
    'created': {
        'type': 'string', 'format': 'datetimepicker',
        'title': 'Chart creation time',
    },
    'layerOptions': {
        'type': 'object',
        'id': '#layeroptions',
        'name': 'layeroptions',
        'default': {
        },
        'properties': {
            'minZoom': {
                'type': 'number',
                'description': 'Minimum zoom number.',
                'default': 0
            },
            'maxZoom': {
                'type': 'number',
                'description': 'Maximum zoom number.',
                'default': 18
            },
            'maxNativeZoom': {
                'type': 'number',
                'description': 'Maximum zoom number the tiles source has '
                               'available. If it is specified, the tiles '
                               'on all zoom levels higher than '
                               'maxNativeZoom will be loaded from '
                               'maxZoom level and auto-scaled.',
            },
            'tileSize': {
                'type': 'number',
                'description': 'Tile size (width and height in '
                               'pixels, assuming tiles are '
                               'square).',
                'default': 256
            },
            'subdomains': {
                'type': 'string',
                'description': 'Subdomains of the tile service. Can be '
                               'passed in the form of one string (where '
                               'each letter is a subdomain name) or an '
                               'array of strings.',
                'default': '''abc'''
            },
            'errorTileUrl': {
                'type': 'string',
                'description': 'URL to the tile image to show in place '
                               'of the tile that failed to load.',
                'default': ''
            },
            'attribution': {
                'type': 'string',
                'description': 'e.g. "&copy; Openstreetmap" - the string '
                               'used by the attribution control, '
                               'describes the layer data.',
                'default': ''
            },
            'tms': {
                'type': 'boolean',
                'description': 'If true, inverses Y axis numbering for '
                               'tiles (turn this on for TMS services).',
                'default': False
            },
            'continuousWorld': {
                'type': 'boolean',
                'description': 'If set to true, the tile coordinates '
                               'won''t be wrapped by world width (-180 '
                               'to 180 longitude) or clamped to lie '
                               'within world height (-90 to 90). Use '
                               'this if you use Leaflet for maps that '
                               'don''t reflect the real world (e.g. '
                               'game, indoor or photo maps).',
                'default': False
            },
            'noWrap': {
                'type': 'boolean',
                'description': 'If set to true, the tiles just won''t '
                               'load outside the world width (-180 to '
                               '180 longitude) instead of repeating.',
                'default': False
            },
            'zoomOffset': {
                'type': 'number',
                'description': 'The zoom number used in tile URLs will '
                               'be offset with this value.',
                'default': 0
            },
            'zoomReverse': {
                'type': 'boolean',
                'description': 'If set to true, the zoom number used in '
                               'tile URLs will be reversed (maxZoom - '
                               'zoom instead of zoom)',
                'default': False
            },
            'opacity': {
                'type': 'number',
                'description': 'The opacity of the tile layer.',
                'default': 1.0
            },
            'zIndex': {
                'type': 'number',
                'description': 'The explicit zIndex of the tile '
                               'layer. Not set by default.',
            },
            'unloadInvisibleTiles': {
                'type': 'boolean',
                'description': 'If true, all the tiles that are not '
                               'visible after panning are removed (for '
                               'better performance). true by default on '
                               'mobile WebKit, otherwise false.'
            },
            'updateWhenIdle': {
                'type': 'boolean',
                'description': 'If false, new tiles are loaded during '
                               'panning, otherwise only after it (for '
                               'better performance). true by default on '
                               'mobile WebKit, otherwise false.'
            },
            'detectRetina': {
                'type': 'boolean',
                'description': 'If true and user is on a retina display, '
                               'it will request four tiles of half the '
                               'specified size and a bigger zoom level '
                               'in place of one to utilize the high '
                               'resolution.'
            },
            'reuseTiles': {
                'type': 'boolean',
                'description': 'If true, all the tiles that are not '
                               'visible after panning are placed in a '
                               'reuse queue from which they will be '
                               'fetched when new tiles become visible ('
                               'as opposed to dynamically creating new '
                               'ones). This will in theory keep memory '
                               'usage low and eliminate the need for '
                               'reserving new memory whenever a new tile '
                               'is needed.'
            },
            'bounds': {
                'type': 'array',
                'description': 'When this option is set, the TileLayer '
                               'only loads tiles that are in the given '
                               'geographical bounds.',
                'items': {
                    'type': 'array',
                    'maxItems': 2,
                    'items': {
                        'type': 'number',
                        'maxItems': 2,
                        'minItems': 2,
                    }
                }
            }
        }
    }
})

Layer = {'schema': LayerSchema, 'form': defaultform}

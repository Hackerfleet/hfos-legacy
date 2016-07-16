"""

Schema: Layer
=============

Contains
--------

Layer: General and renderer specific layer configuration data.

See also
--------

Provisions

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import defaultform

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

LayerSchema = {
    'type': 'object',
    'id': '#layer',
    'name': 'layer',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36, 'title': 'Unique Layer ID',
                 'description': 'HIDDEN'},
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
                 'description': 'Name of view'},
        'owner': {'type': 'string', 'minLength': 36,
                  'title': "Owner's Unique ID", 'description': 'HIDDEN'},
        'color': {'type': 'string', 'title': 'View Color', 'format': 'color',
                  'description': 'This views color indicator'},
        'shared': {'type': 'boolean', 'title': 'Shared view',
                   'description': 'Share view with the crew'},
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                  'description': 'Custom user notes'},
        'cached': {'type': 'boolean', 'title': 'Use tilecache',
                   'description': 'Cache all downloaded map data'},
        'baselayer': {'type': 'boolean', 'title': 'Can be baselayer',
                      'description': 'Baselayer (can be the first layer of a '
                                     'group)'},
        'cachesize': {'type': 'number',
                      'description': 'Current size of cache.'},
        'url': {'type': 'string', 'format': 'html', 'title': 'User notes',
                'description': 'Layer URL'},
        'layerOptions': {
            'minZoom': {'type': 'number',
                        'description': 'Minimum zoom number.', 'default': 0},
            'maxZoom': {'type': 'number',
                        'description': 'Maximum zoom number.', 'default': 18},
            'maxNativeZoom': {'type': 'number',
                              'description': 'Maximum zoom number the tiles '
                                             'source has available. If it is '
                                             'specified,\
                               the tiles on all zoom levels higher than '
                                             'maxNativeZoom will be loaded '
                                             'from maxZoom level\
                               and auto-scaled.',
                              'default': 'null'},
            'tileSize': {'type': 'number',
                         'description': 'Tile size (width and height in '
                                        'pixels, assuming tiles are square).',
                         'default': 256},
            'subdomains': {'type': 'string',
                           'description': 'Subdomains of the tile service. '
                                          'Can be passed in the form of one '
                                          'string\
                            (where each letter is a subdomain name) or an '
                                          'array of strings.',
                           'default': '''abc'''},
            'errorTileUrl': {'type': 'string',
                             'description': 'URL to the tile image to show '
                                            'in place of the tile that '
                                            'failed to load.',
                             'default': ''},
            'attribution': {'type': 'string',
                            'description': 'e.g. "&copy; Openstreetmap" - '
                                           'the string used by the '
                                           'attribution control,\
                             describes the layer data.',
                            'default': ''},
            'tms': {'type': 'boolean',
                    'description': 'If true, inverses Y axis numbering for '
                                   'tiles (turn this on for TMS services).',
                    'default': False},
            'continuousWorld': {'type': 'boolean',
                                'description': 'If set to true, the tile '
                                               'coordinates won''t be '
                                               'wrapped by world width\
                                 (-180 to 180 longitude) or clamped to lie '
                                               'within world height (-90 to '
                                               '90). Use this\
                                 if you use Leaflet for maps that don''t '
                                               'reflect the real world (e.g. '
                                               'game, indoor or\
                                 photo maps).',
                                'default': False},
            'noWrap': {'type': 'boolean',
                       'description': 'If set to true, the tiles just won''t '
                                      'load outside the world width (-180 to\
                        180 longitude) instead of repeating.',
                       'default': False},
            'zoomOffset': {'type': 'number',
                           'description': 'The zoom number used in tile URLs '
                                          'will be offset with this value.',
                           'default': 0},
            'zoomReverse': {'type': 'boolean',
                            'description': 'If set to true, the zoom number '
                                           'used in tile URLs will be reversed\
                             (maxZoom - zoom instead of zoom)',
                            'default': False},
            'opacity': {'type': 'number',
                        'description': 'The opacity of the tile layer.',
                        'default': 1.0},
            'zIndex': {'type': 'number',
                       'description': 'The explicit zIndex of the tile '
                                      'layer. Not set by default.',
                       'default': 'null'},
            'unloadInvisibleTiles': {'type': 'boolean',
                                     'description': 'If true, all the tiles '
                                                    'that are not visible '
                                                    'after panning are\
                                      removed (for better performance). true '
                                                    'by default on mobile '
                                                    'WebKit, otherwise\
                                      false.'},
            'updateWhenIdle': {'type': 'boolean',
                               'description': 'If false, new tiles are '
                                              'loaded during panning, '
                                              'otherwise only after it\
                                (for better performance). true by default on '
                                              'mobile WebKit, otherwise '
                                              'false.'},
            'detectRetina': {'type': 'boolean',
                             'description': 'If true and user is on a retina '
                                            'display, it will request four '
                                            'tiles of\
                              half the specified size and a bigger zoom '
                                            'level in place of one to '
                                            'utilize the\
                              high resolution.'},
            'reuseTiles': {'type': 'boolean',
                           'description': 'If true, all the tiles that are '
                                          'not visible after panning are '
                                          'placed in a\
                            reuse queue from which they will be fetched when '
                                          'new tiles become visible (as '
                                          'opposed to\
                            dynamically creating new ones). This will in '
                                          'theory keep memory usage low and '
                                          'eliminate\
                            the need for reserving new memory whenever a new '
                                          'tile is needed.'},
            'bounds': {'type': 'list',
                       'description': 'When this option is set, the TileLayer only loads tiles that are in the given\
                        geographical bounds.'}
        }
    }
}

Layer = {'schema': LayerSchema, 'form': defaultform}

"""
Schema: Vessel
==============

Contains
--------

Vessel: Vesselprofile to store Vessel specific settings

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

VesselSchema = {
    'id': '#Vessel',
    'type': 'object',
    'name': 'Vessel',
    'properties': {
        'uuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                 'type': 'string',
                 'title': 'Unique Vessel ID'
                 },
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name', 'description': 'Vessel name'},
        'vesseltype': {'type': 'string', 'title': 'Vessel Type', 'enum': ['Sailboat', 'Motorboat', 'Platform'],
                       'description': 'General classification of vessel'},
        'color': {'type': 'string', 'title': 'Vessel Color', 'format': 'color',
                  'description': 'Color used for map annotations etc'},
        'registration': {'type': 'string', 'minLength': 1, 'title': 'Registration',
                         'description': 'Official registration'},
        'origin': {'type': 'string', 'minLength': 1, 'title': 'Country of origin',
                   'description': 'Registration country'},
        'loa': {'type': 'number', 'title': 'LOA', 'description': 'Length-over-all'},
        'lwl': {'type': 'number', 'title': 'LWL', 'description': 'Length-water-line'},
        'beam': {'type': 'number', 'title': 'Beam', 'description': 'Breadth amidships'},
        'draft': {'type': 'number', 'title': 'Draft',
                  'description': "Static depth of a vessel's keel below watersurface"},
        'height-max': {'type': 'number', 'title': 'Height (raised)',
                       'description': 'Maximal vessel height'},
        'height-min': {'type': 'number', 'title': 'Height (lowered)',
                       'description': 'Minimal vessel height'},
        'motors': {'type': 'number', 'title': 'Engines', 'description': 'Count of engines'},
        'motorpower': {'type': 'number', 'title': 'Enginepower', 'description': 'Cumulative engine power'},
        'sailplan': {'type': 'string', 'title': 'Sail-plan', 'description': 'Sail-plan configuration',
                     'enum': ['Barque', 'Barquentine/Schooner barque', 'Bragana/Felucca', 'Catboat',
                              'Cutter', 'Gunter', 'Hermaphrodite Brig/Schooner Brig', 'Ketch',
                              'Polacre', 'Proa', 'Schooner', 'Sloop', 'Snow', 'Sunfish',
                              'Topsail Schooner', 'Two-topsail Schooner', 'Yawl'
                              ]
                     },
        'hullplan': {'type': 'string', 'title': 'Hull-plan', 'description': 'Hull-plan configuration',
                     'enum': ['Monohull', 'Catamaran', 'Trimaran', 'Quadrimaran', 'Pentamaran']
                     },
        'water-production': {'type': 'number', 'title': 'Water (production)',
                             'description': 'Potable water production l/day'},
        'water-storage': {'type': 'number', 'title': 'Water (storage)',
                          'description': 'Potable water storage capacity'},
        'fuel-storage': {'type': 'number', 'title': 'Fuel (storage)',
                         'description': 'Fuel storage capacity'},
        'fuel-consumption': {'type': 'number', 'title': 'Fuel (consumption)',
                             'description': 'Maximum fuel consumption per hour'},
        'waste-storage': {'type': 'number', 'title': 'Wastewater (storage)',
                          'description': 'Waste water storage capacity'},
        'cabins': {'type': 'number', 'title': 'Cabin count', 'description': 'Crew cabins'},
        'bunks': {'type': 'number', 'title': 'Bunk count', 'description': 'Crew bunks'},
        'description': {'type': 'string', 'format': 'html', 'title': 'Vessel description',
                        'description': 'Freeform vessel description'},
    }
}

VesselForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-3',
                'items': [
                    'name', 'loa', 'height-max', 'hullplan', 'fuel-storage', 'color'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-3',
                'items': [
                    'registration', 'lwl', 'height-min', 'sailplan', 'fuel-consumption'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-3',
                'items': [
                    'vesseltype', 'draft', 'motors', 'cabins', 'water-storage'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-3',
                'items': [
                    'origin', 'beam', 'motorpower', 'bunks', 'water-production', 'waste-storage'
                ]
            }

        ]
    },
    'description',
    {
        'type': 'submit',
        'title': 'Save Vessel data',
    }
]

__schema__ = VesselSchema
__form__ = VesselForm

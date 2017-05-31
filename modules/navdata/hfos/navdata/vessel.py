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
Schema: Vessel
==============

Contains
--------

Vessel: Vesselprofile to store Vessel specific settings


"""
from hfos.schemata.base import base_object

VesselSchema = base_object('vessel')

VesselSchema['properties'].update({
    'mapviewuuid': {
        'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-['
                   'a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                   'a-fA-F0-9]{12}$',
        'type': 'string',
        'title': 'Unique Vessel Moving Mapview ID'
    },
    'details': {
        'type': 'object',
        'oneOf': [
            {
                'type': 'object',
                'title': 'Seafaring Vessel',
                'properties': {
                    'mmsi': {'type': 'string', 'minLength': 9, 'maxLength': 9,
                             'title': 'MMSI',
                             'description': 'Martime Mobile Service Identity'},
                    'vesseltype': {'type': 'string', 'title': 'Vessel Type',
                                   'enum': ['Sailboat', 'Motorboat',
                                            'Platform'],
                                   'description': 'General classification of '
                                                  'vessel'},
                    'color': {'type': 'string', 'title': 'Vessel Color',
                              'format': 'color',
                              'description': 'Color used for annotations'},
                    'registration': {'type': 'string', 'minLength': 1,
                                     'title': 'Registration',
                                     'description': 'Official registration'},
                    'origin': {'type': 'string', 'minLength': 1,
                               'title': 'Country of origin',
                               'description': 'Registration country'},
                    'hullplan': {'type': 'string', 'title': 'Hull-plan',
                                 'description': 'Hull-plan configuration',
                                 'enum': ['Monohull', 'Catamaran', 'Trimaran',
                                          'Quadrimaran', 'Pentamaran']
                                 },
                    'loa': {'type': 'number', 'title': 'LOA',
                            'description': 'Length-over-all'},
                    'lwl': {'type': 'number', 'title': 'LWL',
                            'description': 'Length-water-line'},
                    'beam': {'type': 'number', 'title': 'Beam',
                             'description': 'Breadth amidships'},
                    'draft': {'type': 'number', 'title': 'Draft',
                              'description': "Static depth of a vessel's "
                                             "keel below watersurface"},
                    'height-max': {'type': 'number',
                                   'title': 'Height (raised)',
                                   'description': 'Maximal vessel height'},
                    'height-min': {'type': 'number',
                                   'title': 'Height (lowered)',
                                   'description': 'Minimal vessel height'},
                    'motors': {'type': 'number', 'title': 'Engines',
                               'description': 'Count of engines'},
                    'motorpower': {'type': 'number', 'title': 'Enginepower',
                                   'description': 'Cumulative engine power'},
                    'sailplan': {'type': 'string', 'title': 'Sail-plan',
                                 'description': 'Sail-plan configuration',
                                 'enum': ['Barque',
                                          'Barquentine/Schooner barque',
                                          'Bragana/Felucca', 'Catboat',
                                          'Cutter', 'Gunter',
                                          'Hermaphrodite Brig/Schooner Brig',
                                          'Ketch',
                                          'Polacre', 'Proa', 'Schooner',
                                          'Sloop', 'Snow', 'Sunfish',
                                          'Topsail Schooner',
                                          'Two-topsail Schooner', 'Yawl'
                                          ]
                                 },
                    'sailarea': {'type': 'number', 'title': 'Sail area',
                                 'description': 'Maximum unfolded usable '
                                                'sail area (m²)'},
                    'water-production': {'type': 'number',
                                         'title': 'Water (production)',
                                         'description': 'Potable water '
                                                        'production l/day'},
                    'water-storage': {'type': 'number',
                                      'title': 'Water (storage)',
                                      'description': 'Potable water storage '
                                                     'capacity'},
                    'fuel-storage': {'type': 'number',
                                     'title': 'Fuel (storage)',
                                     'description': 'Fuel storage capacity'},
                    'fuel-consumption': {'type': 'number',
                                         'title': 'Fuel (consumption)',
                                         'description': 'Maximum fuel '
                                                        'consumption per '
                                                        'hour'},
                    'waste-storage': {'type': 'number',
                                      'title': 'Wastewater (storage)',
                                      'description': 'Waste water storage '
                                                     'capacity'},
                    'cabins': {'type': 'number', 'title': 'Cabin count',
                               'description': 'Crew cabins'},
                    'bunks': {'type': 'number', 'title': 'Bunk count',
                              'description': 'Crew bunks'},
                    'description': {'type': 'string', 'format': 'html',
                                    'title': 'Vessel description',
                                    'description': 'Freeform vessel '
                                                   'description'},
                }
            }
        ]
    }
})

VesselForm = [
    {
        'type': 'tabs',
        'tabs': [
            {
                'title': 'General',
                'items': [
                    {
                        'type': 'section',
                        'htmlClass': 'row',
                        'items': [
                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-4',
                                'items': [
                                    'name', 'vesseltype', 'hullplan'
                                ]
                            },
                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-4',
                                'items': [
                                    'color', 'registration'
                                ]
                            },
                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-4',
                                'items': [
                                    'mmsi', 'origin'
                                ]
                            }
                        ]
                    }

                ],
            },
            {
                'title': 'Geometry',
                'items': [
                    {
                        'type': 'section',
                        'htmlClass': 'row',
                        'items': [
                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-4',
                                'items': [
                                    'loa', 'draft', 'height-max'
                                ]
                            },
                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-4',
                                'items': [
                                    'lwl', 'beam', 'height-min'
                                ]
                            },

                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-4',
                                'items': [
                                    'cabins', 'bunks'
                                ]
                            }
                        ]
                    },
                ]
            },
            {
                'title': 'Sails & Engines',
                'items': [
                    {
                        'type': 'section',
                        'htmlClass': 'row',
                        'items': [
                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-6',
                                'items': [
                                    'motors', 'sailplan'
                                ]
                            },
                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-6',
                                'items': [
                                    'motorpower', 'sailarea'
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                'title': 'Bunkers & Consumption',
                'items': [
                    {
                        'type': 'section',
                        'htmlClass': 'row',
                        'items': [
                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-6',
                                'items': [
                                    'fuel-storage', 'water-storage',
                                    'waste-storage'
                                ]
                            },
                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-6',
                                'items': [
                                    'fuel-consumption', 'water-production'
                                ]
                            }
                        ]
                    }
                ]
            }

        ]
    },
    'description',
    {
        'type': 'button',
        'onClick': '$ctrl.submitObject()',
        'title': 'Save Vessel data',
    }
]

VesselData = {'schema': VesselSchema, 'form': VesselForm}

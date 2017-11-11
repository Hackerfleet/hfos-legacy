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
    'sog': {'type': 'number', 'title': 'SOG',
            'description': 'Speed over ground (kn)'},
    'cog': {'type': 'number', 'title': 'COG',
            'description': 'Course over ground (rel. to true North)'},
    'rot': {'type': 'number', 'title': 'ROT',
            'description': 'Rate of turn (+-720°/min)'},
    'true_heading': {'type': 'number', 'title': 'True heading',
                     'description': 'True heading (0°-359°)'},
    'true_bearing': {'type': 'number', 'title': 'True bearing',
                     'description': 'True bearing at own position (0°-359°'},
    'geojson': {
        'type': 'object',
        'default': {
            'type': 'Point',
            'coordinates': [0.0, 0.0]
        },
        'properties': {
            "type": {
                'enum': ['Point']
            },
            'accuracy': {
                'type': 'array',
                'title': 'Accuracy',
                'description': 'Positional Accuracy (Lon/Lat)',
                'default': [0.0, 0.0],
                'items': {
                    'type': 'number',
                    'minItems': 2,
                    'maxItems': 2
                }
            },
            "coordinates": {
                'type': 'array',
                # TODO: Decide if we want to integrate null island as default
                'default': [0.0, 0.0],
                'items': {
                    'type': 'number',
                    'minItems': 2,
                    'maxItems': 2
                }
            }
        }
    },
    'source': {
        'type': 'string',
        'title': 'Source',
        'enum': ['AIS', 'OSDM', 'SIM'],
        'description': 'Data source for this vessel'
    },
    'description': {
        'type': 'string', 'format': 'html',
        'title': 'Vessel description',
        'description': 'Freeform vessel '
                       'description'
    },
    'color': {
        'type': 'string', 'title': 'Vessel Color',
        'format': 'color',
        'description': 'Color used for annotations'
    },
    'details': {
        'type': 'object',
        'properties':
            {
                # 'type': 'object',
                # 'title': 'Seafaring Vessel',
                # 'properties': {
                'mmsi': {'type': 'string', 'minLength': 9, 'maxLength': 9,
                         'title': 'MMSI',
                         'description': 'Maritime Mobile Service '
                                        'Identity'},
                'imo_sin': {'type': 'string', 'minLength': 7, 'maxLength': 7,
                            'title': 'IMO SIN',
                            'description': 'IMO Ship identification number'},
                'vessel_type': {'type': 'string', 'title': 'Vessel Type',
                                'enum': ['Sailboat', 'Motorboat',
                                         'Platform'],
                                'description': 'General classification of '
                                               'vessel'},
                'registration': {'type': 'string', 'minLength': 1,
                                 'title': 'Registration',
                                 'description': 'Official registration'},
                'origin': {'type': 'string', 'minLength': 1,
                           'title': 'Country of origin',
                           'description': 'Registration country'},
                'call_sign': {'type': 'string', 'minLength': 1,
                              'title': 'Call sign',
                              'description': 'Radio call sign/number'},
                'contact_mail': {'type': 'string', 'minLength': 1,
                                 'title': 'Contact email',
                                 'description': 'Emergency email contact'},
                'contact_phone': {'type': 'string', 'minLength': 1,
                                  'title': 'Contact phone',
                                  'description': 'Emergency '
                                                 'phone/sat contact'},
                'year_built': {'type': 'integer', 'title': 'Year built',
                               'description': 'Year of vessel '
                                              'construction'},
                'hull_plan': {'type': 'string', 'title': 'Hull-plan',
                              'description': 'Hull-plan configuration',
                              'enum': ['Monohull', 'Catamaran', 'Trimaran',
                                       'Quadrimaran', 'Pentamaran']
                              },
                'features': {'type': 'string', 'format': 'html',
                             'title': 'Features', 'minLength': 1,
                             'description': 'Prominent features'},
                'loa': {'type': 'number', 'title': 'LOA',
                        'description': 'Length-over-all (m)'},
                'lwl': {'type': 'number', 'title': 'LWL',
                        'description': 'Length-water-line (m)'},
                'beam': {'type': 'number', 'title': 'Beam',
                         'description': 'Breadth amidships (m)'},
                'draft': {'type': 'number', 'title': 'Draft',
                          'description': "Static depth of a vessel's "
                                         "keel below watersurface (m)"},
                'height_max': {'type': 'number',
                               'title': 'Height raised',
                               'description': 'Maximal vessel height (m)'},
                'height_min': {'type': 'number',
                               'title': 'Height (lowered)',
                               'description': 'Minimal vessel height (m)'},
                'motor_count': {'type': 'number', 'title': 'Engines',
                                'description': 'Count of engines'},
                'motor_power': {'type': 'number', 'title': 'Enginepower',
                                'description': 'Cumulative engine power (kW)'},
                'sail_plan': {'type': 'string', 'title': 'Sail-plan',
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
                'sail_area': {'type': 'number', 'title': 'Sail area',
                              'description': 'Maximum unfolded usable '
                                             'sail area (m²)'},
                'hull_color': {'type': 'string', 'format': 'colorpicker',
                               'title': 'Prominent hull color',
                               'description': 'Most prominent hull color '
                                              'of '
                                              'Vessel'},
                'hull_material': {'type': 'string', 'title': 'Hull '
                                                             'material',
                                  'description': 'Construction material '
                                                 'of the hull',
                                  'enum': ['CFK', 'GFK', 'Aluminium',
                                           'Steel', 'Wood', 'Concrete',
                                           'Plastics']
                                  },
                'water_production': {'type': 'number',
                                     'title': 'Water (production)',
                                     'description': 'Potable water '
                                                    'production l/day'},
                'water_storage': {'type': 'number',
                                  'title': 'Water (storage)',
                                  'description': 'Potable water storage '
                                                 'capacity (l)'},
                'fuel_storage': {'type': 'number',
                                 'title': 'Fuel (storage)',
                                 'description': 'Fuel storage capacity (l)'},
                'fuel_consumption': {'type': 'number',
                                     'title': 'Fuel (consumption)',
                                     'description': 'Maximum fuel '
                                                    'consumption per '
                                                    'hour (l)'},
                'waste_storage': {'type': 'number',
                                  'title': 'Wastewater (storage)',
                                  'description': 'Waste water storage '
                                                 'capacity (l)'},
                'cabins': {'type': 'number', 'title': 'Cabin count',
                           'description': 'Crew cabins'},
                'bunks': {'type': 'number', 'title': 'Bunk count',
                          'description': 'Crew bunks'},

                # }
            }
        # ]
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
                                    'name', {
                                        'key': 'details.vessel_type',
                                        'placeholder': 'Select Vessel type'
                                    },
                                    {
                                        'key': 'details.hull_plan',
                                        'placeholder': 'Select hull plan'
                                    }
                                ]
                            },
                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-4',
                                'items': [
                                    'color', 'details.registration',
                                    'details.year_built'
                                ]
                            },
                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-4',
                                'items': [
                                    'details.mmsi', 'details.origin',
                                    'details.call_sign'
                                ]
                            }
                        ]
                    },
                    'description'

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
                                    'details.loa', 'details.draft',
                                    'details.height_max',
                                    {
                                        'key': 'details.hull_material',
                                        'placeholder': 'Select hull material'
                                    }
                                ]
                            },
                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-4',
                                'items': [
                                    'details.lwl', 'details.beam',
                                    'details.height_min', 'details.hull_color'
                                ]
                            },

                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-4',
                                'items': [
                                    'details.cabins', 'details.bunks',
                                    'details.features'
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
                                    'details.motor_count',
                                    {
                                        'key': 'details.sail_plan',
                                        'placeholder': 'Select sail plan'
                                    }
                                ]
                            },
                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-6',
                                'items': [
                                    'details.motor_power', 'details.sail_area'
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
                                    'details.fuel_storage',
                                    'details.water_storage',
                                    'details.waste_storage'
                                ]
                            },
                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-6',
                                'items': [
                                    'details.fuel_consumption',
                                    'details.water_production'
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                'title': 'Safety & Emergencies',
                'items': [
                    {
                        'type': 'section',
                        'htmlClass': 'row',
                        'items': [
                            {
                                'type': 'section',
                                'htmlClass': 'col-xs-6',
                                'items': [
                                    'details.contact_mail'
                                ]
                            }, {
                                'type': 'section',
                                'htmlClass': 'col-xs-6',
                                'items': [
                                    'details.contact_phone'
                                ]
                            },
                        ]
                    }
                ]
            }
        ]
    },
    {
        'type': 'button',
        'onClick': '$ctrl.submitObject()',
        'title': 'Save Vessel data',
    }
]

VesselData = {'schema': VesselSchema, 'form': VesselForm}

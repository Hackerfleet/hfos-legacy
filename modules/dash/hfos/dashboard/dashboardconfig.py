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
from hfos.schemata.extends import DefaultExtension

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""
Schema: Dashboard
=================

Contains
--------

Dashboard: Dashboard config to store gridster settings


"""

from hfos.schemata.defaultform import *
from hfos.schemata.base import base_object, uuid_object

DashboardSchema = base_object('dashboardconfig', all_roles='crew')

DashboardSchema['properties'].update({
    'locked': {'type': 'boolean', 'title': 'Locked Dashboard',
               'description': 'Determines whether the Dashboard should '
                              'be locked against changes.'},
    'refreshrate': {'title': 'Refreshrate', 'type': 'number',
                    'description': 'General refresh rate of dashboard'},
    'shared': {'type': 'boolean', 'title': 'Shared Dashboard',
               'description': 'Share Dashboard with the crew'},
    'description': {'type': 'string', 'format': 'html',
                    'title': 'Dashboard description',
                    'description': 'Dashboard description'},
    'cards': {
        'type': 'array',
        'default': [],
        'items': {
            'type': 'object',
            'id': '#Card',
            'name': 'DashboardCard',
            'properties': {
                'widgettype': {
                    'type': 'string',
                    'enum': [
                        'simplebarreadout',
                        'historybarreadout',
                        'digitalreadout',
                        'simplecompass',
                        'linechart',
                        'clock'
                    ]
                },
                'valuetype': {'type': 'string'},
                'sensor': {'type': 'boolean', 'title': 'Sensor',
                           'description': 'This widget reads from any sensordatatype'},
                'title': {'type': 'string'},
                'position': {
                    'type': 'object',
                    'properties': {
                        'x': {'type': 'number'},
                        'y': {'type': 'number'}
                    }
                },
                'size': {
                    'type': 'object',
                    'properties': {
                        'width': {'type': 'number', 'default': 2},
                        'height': {'type': 'number', 'default': 2}
                    }
                },
            }
        }
    }
})

DashboardForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'name', 'refreshrate'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'shared', 'locked'
                ]
            },
        ]
    },
    {
        'key': 'cards',
        'add': "Add widget",
        'style': {
            'add': "btn-success"
        },
        'items': [
            'cards[].title',
            'cards[].widgettype',
            lookup_field('cards[].valuetype', 'sensordatatype', 'Select a Sensor Value', 'name',
                         select_type='uiselect'),
        ],
        'startEmpty': True,
    },
    'description',
    editbuttons
]

DashboardExtends = DefaultExtension(
    {'dashboarduuid': uuid_object('Default Dashboard')},
    lookup_field('modules.dashboarduuid', 'dashboardconfig')
)

DashboardConfig = {'schema': DashboardSchema, 'form': DashboardForm, 'extends': DashboardExtends}

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

Schema: WateringRule
============

Contains
--------

WateringRule reference entry for the garden to set up pump start times and
durations as well as conditions..


"""
from hfos.schemata.base import base_object

WateringRuleSchema = base_object('wateringrule', all_roles='crew')

WateringRuleSchema['properties'].update({
    'status': {
        'type': 'bool',
        'title': 'Status',
        'description': 'If watering rule is active'
    },
    'notes': {
        'type': 'string',
        'format': 'html',
        'title': 'User notes',
        'description': 'Entry notes'
    },
    'activationtime': {
        'type': 'string',
        'description': 'Activation time of watering rule'
    },
    'duration': {'type': 'number', 'description': 'Duration of pump '
                                                  'activation'}
})

WateringRuleForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'name', 'activationtime'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'status', 'duration'

                ]
            },
        ]
    },
    'notes',
    {
        'key': 'Toggle',
        'type': 'button',
        'onClick': 'formAction("hfos.garden", "toggle", model.uuid)',
        'title': 'Toggle WateringRule'
    },
    {
        'key': 'Suspend',
        'type': 'button',
        'condition': 'model.status',
        'onClick': 'formAction("hfos.garden", "suspend", model.uuid)',
        'title': 'Suspend the rule for the next time'
    },
    {
        'type': 'submit',
        'title': 'Save Watering Rule',
    }
]

WateringRule = {'schema': WateringRuleSchema, 'form': WateringRuleForm}

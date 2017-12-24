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

Schema: Equipment
=================

Contains
--------

Equipment specifications

"""

from hfos.schemata.defaultform import editbuttons
from hfos.schemata.base import base_object

EquipmentSchema = base_object('equipment', all_roles='crew')

StatusEnums = ['Okay', 'Not quite right',
               'Broken', 'Maintenance', 'Needs attention']

EquipmentSchema['properties'].update({
    'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
              'description': 'Entry notes'},
    'status': {
        'type': 'string', 'title': 'Status',
        'description': 'Current status of equipment',
        'enum': StatusEnums
    },
    'alerts': {
        'type': 'array',
        'default': [],
        'items': {
            'type': 'object',
            'properties': {
                'mode': {
                    'type': 'string', 'title': 'Mode',
                    'description': 'Mode of alert',
                    'enum': ['Timespan', 'Travelled distance', 'Motor hours',
                             'System Status change']
                },
                'status_next': {
                    'type': 'string',
                    'title': 'Next status',
                    'description': 'Set to this status on alert',
                    'enum': StatusEnums
                },
                'status_previous': {
                    'type': 'array',
                    'title': 'Previous status',
                    'description': 'Alert can only trigger while on this '
                                   'status',

                    'items': {
                        'type': 'string',
                        'enum': StatusEnums + ["Don't change"]
                    },
                    'default': []
                },
                'action': {
                    'type': 'string',
                    'title': 'Alert action text',
                    'description': 'Instructions to supply alert with (e.g. '
                                   '"Check oil")',
                    'default': ''
                },
                'start': {
                    'type': 'string',
                    'format': 'datetimepicker',
                    'title': 'Initial alert start',
                    'description': 'The point in time when the alert '
                                   'began measuring'
                },
                'interval': {
                    'type': 'integer',
                    'title': 'Interval',
                    'description': 'Interval of alert in hours or KM'
                },
                'state_old': {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'title': 'Old states',
                        'description': 'Alert can only trigger while on '
                                       'any of the old system states',
                    },
                    'default': []
                },
                'state_new': {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'title': 'New states',
                        'description': 'Alert can only trigger when '
                                       'switching to any of these system '
                                       'states',
                    },
                    'default': []
                }
            }
        }
    }
})

StatusChangeForm = {
    'type': 'section',
    'htmlClass': 'row',
    'condition': "$ctrl.model.alerts[arrayIndex].mode == "
                 "'System Status change'",
    'items': [
        {
            'type': 'section',
            'htmlClass': 'col-xs-6',
            'items': [
                {
                    'key': 'alerts[].state_old',
                    'add': 'Add state',
                    'startEmpty': True,
                    'style': {
                        'add': 'btn-success'
                    },
                    'items': [
                        {
                            'key': 'alerts[].state_old[]',
                            'type': 'strapselect',
                            'placeholder': 'Select the old states',
                            'options': {
                                "type": "nodestate",
                                "asyncCallback": "$ctrl.getFormData",
                                "map": {
                                    'valueProperty': "uuid",
                                    'nameProperty': 'name'
                                }
                            }
                        }
                    ]
                }
            ],
        },
        {
            'type': 'section',
            'htmlClass': 'col-xs-6',
            'items': [
                {
                    'key': 'alerts[].state_new',
                    'add': 'Add state',
                    'startEmpty': True,
                    'style': {
                        'add': 'btn-success'
                    },
                    'items': [
                        {
                            'key': 'alerts[].state_new[]',
                            'type': 'strapselect',
                            'placeholder': 'Select the new states',
                            'options': {
                                "type": "nodestate",
                                "asyncCallback": "$ctrl.getFormData",
                                "map": {
                                    'valueProperty': "uuid",
                                    'nameProperty': 'name'
                                }
                            }
                        }
                    ]
                }
            ]
        }
    ]
}

EquipmentForm = [{
    'type': 'tabs',
    'tabs': [
        {
            'title': 'Equipment definition',
            'items': [
                {
                    'type': 'section',
                    'htmlClass': 'row',
                    'items': [
                        {
                            'type': 'section',
                            'htmlClass': 'col-xs-9',
                            'items': [
                                'name'
                            ]
                        },
                        {
                            'type': 'section',
                            'htmlClass': 'col-xs-3',
                            'items': [
                                {
                                    'key': 'status',
                                    'placeholder': 'Select status'
                                }
                            ]
                        }
                    ]
                },
                'notes'
            ]
        },
        {
            'title': 'Alerts',
            'type': 'fieldset',
            'items': [
                {
                    'key': 'alerts',
                    'add': 'Add Alert',
                    'startEmpty': True,
                    'style': {
                        'add': 'btn-success'
                    },
                    'items': [
                        {
                            'type': 'section',
                            'htmlClass': 'row',
                            'items': [
                                {
                                    'type': 'section',
                                    'htmlClass': 'col-xs-4',
                                    'items': [
                                        'alerts[].mode'
                                    ]
                                },
                                {
                                    'type': 'section',
                                    'htmlClass': 'col-xs-4',
                                    'items': [
                                        'alerts[].status_previous',

                                    ]
                                }, {
                                    'type': 'section',
                                    'htmlClass': 'col-xs-4',
                                    'items': [
                                        'alerts[].status_next'
                                    ]
                                },
                            ]
                        },
                        {
                            'type': 'section',
                            'htmlClass': 'row',
                            'items': [
                                {
                                    'type': 'section',
                                    'condition': "$ctrl.model.alerts["
                                                 "arrayIndex].mode != "
                                                 "'System "
                                                 "Status change'",
                                    'htmlClass': 'col-xs-4',
                                    'items': [
                                        'alerts[].start',
                                        'alerts[].interval'
                                    ]
                                },
                                StatusChangeForm
                            ]
                        },
                        {
                            'key': 'alerts[].action',
                        }
                    ]
                }
            ]
        }
    ]
}, editbuttons]

Equipment = {'schema': EquipmentSchema, 'form': EquipmentForm}

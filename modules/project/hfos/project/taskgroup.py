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

Schema: Task
============

Contains
--------

Task reference entry for the todo management

See also
--------

Provisions


"""

from hfos.schemata.extends import DefaultExtension
from hfos.schemata.defaultform import lookup_field, editbuttons
from hfos.schemata.base import uuid_object, base_object

TaskGroupSchema = base_object('taskgroup', all_roles='crew')

TaskGroupSchema['properties'].update({
    'project': {'type': 'string', 'title': 'Project',
                'description': 'Project, the Task Group belongs to'},
    'creator': {'type': 'string', 'title': 'Creator',
                'description': 'Creator of Task Group'},
    'tags': {'type': 'string', 'title': 'Tags',
             'description': 'Attached tags'},
    'color': {'type': 'string', 'title': 'Task Group Color',
              'format': 'color',
              'description': 'Color used for this Task Group'},
    'priority': {'type': 'number', 'title': 'Priority',
                 'description': '1 is Highest priority', 'minimum': 1},
    'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
              'description': 'Entry notes'},
})

TaskGroupForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'name', 'tags', {
                        'key': 'project',
                        'type': 'strapselect',
                        'placeholder': 'Select a Project',
                        'options': {
                            "type": "project",
                            "asyncCallback": "$ctrl.getFormData",
                            "map": {'valueProperty': "uuid",
                                    'nameProperty': 'name'}
                        }
                    }
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'color', 'priority'
                ]
            },
        ]
    },
    'notes',
    {
        'type': 'fieldset',
        'items': [
            {
                'key': 'references',
                'add': 'Add Reference',
                'style': {
                    'add': 'btn-success'
                },
                'items': [
                    "references[].referencetype",
                    {
                        'key': 'references[].task',
                        'type': 'strapselect',
                        'placeholder': 'Select a Project',
                        'options': {
                            "type": "task",
                            "asyncCallback": "$ctrl.getFormData",
                            "map": {'valueProperty': "uuid",
                                    'nameProperty': 'name'}
                        }
                    }
                ]
            }
        ]
    },
    editbuttons
]

TaskgroupExtends = DefaultExtension(
    {
        'closed_group': uuid_object('Default "Closed" group', default=['f7525ffb-0f30-4654-bb72-602fb17247af']),
    # Taskgroup "Closed"
        'open_groups': {
            'type': 'array',
            'title': 'Open Groups',
            'description': 'Taskgroups with open tasks for Todo list',
            'default': [
                "52fc2c8d-bf7a-4835-bbfe-82d3ddf3742f",  # Taskgroup "New"
                "9d7f146e-1307-47d5-a2cf-bc26f0f515d5",  # Taskgroup "In progress"
            ],
            'items': uuid_object('Open groups')
        }
    },
    [
        lookup_field('modules.closed_group', 'taskgroup', 'Select a group for closed tasks'),
        {
            'key': 'modules.open_groups',
            'type': 'strapselect',
            'placeholder': 'Select taskgroups',
            'options': {
                "multiple": 'true',
                "type": "taskgroup",
                "asyncCallback": "$ctrl.getFormData",
                "map": {
                    'valueProperty': "uuid",
                    'nameProperty': 'name'
                }
            }
        }
        # {
        #    'key': 'modules.open_groups',
        #    'startEmpty': True,
        #    'add': 'Add Taskgroup',
        #    'style': {
        #        'add': 'btn-success'
        #    },
        #    'items': [
        #        lookup_field('modules.open_groups[].uuid', 'taskgroup', 'Select a taskgroup')
        #    ]
        # }
    ]
)

TaskGroup = {'schema': TaskGroupSchema, 'form': TaskGroupForm, 'extends': TaskgroupExtends}

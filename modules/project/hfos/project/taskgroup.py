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

Schema: Task
============

Contains
--------

Task reference entry for the todo management

See also
--------

Provisions


"""

from hfos.schemata.defaultform import editbuttons
from hfos.schemata.base import base_object

TaskGroupSchema = base_object('taskgroup', all_roles='crew')

TaskGroupSchema['properties'].update({
    'project': {'type': 'string', 'title': 'Project',
                'description': 'Project, the Task Group belongs to'},
    'creator': {'type': 'string', 'title': 'Creator',
                'description': 'Creator of Task Group'},
    'tags': {'type': 'string', 'title': 'Tags',
             'description': 'Attached tags'},
    'color': {'type': 'string', 'title': 'Task Group Color',
              # 'format': 'color',
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

TaskGroup = {'schema': TaskGroupSchema, 'form': TaskGroupForm}

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

from hfos.schemata.defaultform import editbuttons, section, lookup_field
from hfos.schemata.tag import TagData, TagForm
from hfos.schemata.base import base_object, uuid_object

TaskSchema = base_object('task', all_roles='crew')

TaskSchema['properties'].update({
    'project': uuid_object('Project which this task is part of', 'Select a project'),
    'creator': uuid_object('Creator', 'Select a creator'),
    'assignee': uuid_object('Assignee', 'Select an assignee'),
    'taskgroup': uuid_object(title='Task group', description='Group, this task belongs to'),
    'tags': TagData,
    'alert_time': {'type': 'string', 'title': 'Alert',
                   'format': 'datetimepicker',
                   'description': 'Alert time'},
    'due_time': {'type': 'string', 'title': 'Due',
                 'format': 'datetimepicker',
                 'description': 'Due time'},
    'priority': {'type': 'number', 'title': 'Priority',
                 'description': '1 is Highest priority', 'minimum': 1},
    'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
              'description': 'Entry notes', 'default': ''},
    'comments': {
        'type': 'array',
        'default': [],
        'items': {
            'type': 'string',
            'format': 'html',
            'title': 'Comment',
            'description': 'Comment text'
        }
    },
    'references': {
        'type': 'array',
        'default': [],
        'items': {
            'type': 'object',
            'properties': {
                'referencetype': {
                    'type': 'string', 'enum': [
                        'Duplicate',
                        'Epic',
                        'Blocking'
                    ]
                },
                'task': uuid_object(title='Task UUID', description='Referenced Task'),
            }
        }
    },
    'changes': {
        'type': 'array',
        'default': [],
        'items': {
            'type': 'object',
            'properties': {
                'time': {'type': 'string', 'format': 'datetimepicker',
                         'title': 'Time of change',
                         'description': 'Time when this change was '
                                        'accepted'},
                'change': {
                    'type': 'object',
                    'name': '#taskchange',
                    'properties': {
                        'status': {'type': 'string',
                                   'title': 'New status',
                                   'description': 'Status changed to '
                                                  'this status'},
                        'comment': {'type': 'string', 'title': 'Comment',
                                    'description': 'Comment text'},
                        'priority': {'type': 'number',
                                     'title': 'Priority',
                                     'description': '1 is Highest '
                                                    'priority'},
                        'tags': {'type': 'string', 'title': 'Tags',
                                 'description': 'Attached tags'},
                        'notes': {'type': 'string', 'format': 'html',
                                  'title': 'User notes',
                                  'description': 'Entry notes'},
                        'owner': {'type': 'string', 'minLength': 36,
                                  'title': "Owner's Unique ID",
                                  'description': 'HIDDEN'},
                        'name': {'type': 'string', 'title': 'Name',
                                 'description': 'Name of Task'}
                    }

                },
                'creator': uuid_object(title='Unique Creator ID')
            }
        }
    }
})

TaskForm = [
    section(2, 3, [['name', lookup_field('assignee', 'user'), 'priority'],
                   [lookup_field('project'), lookup_field('taskgroup'), 'creator']]),
    section(1, 2, [['alert_date', 'alert_time']]),
    # {
    #     'type': 'section',
    #     'htmlClass': 'row',
    #     'items': [
    #         {
    #             'type': 'section',
    #             'htmlClass': 'col-xs-6',
    #             'items': [
    #                 'name', {
    #                     'key': 'project',
    #                     'type': 'strapselect',
    #                     'placeholder': 'Select a Project',
    #                     'options': {
    #                         "type": "project",
    #                         "asyncCallback": "$ctrl.getFormData",
    #                         "map": {'valueProperty': "uuid",
    #                                 'nameProperty': 'name'}
    #                     }
    #                 }
    #             ]
    #         },
    #         {
    #             'type': 'section',
    #             'htmlClass': 'col-xs-6',
    #             'items': [
    #                 {
    #                     'key': 'owner',
    #                     'type': 'strapselect',
    #                     'placeholder': 'Select a new Owner',
    #                     'options': {
    #                         "type": "user",
    #                         "asyncCallback": "$ctrl.getFormData",
    #                         "map": {'valueProperty': "uuid",
    #                                 'nameProperty': 'name'}
    #                     }
    #                 }, {
    #                     'key': 'assignee',
    #                     'type': 'strapselect',
    #                     'placeholder': 'Select an Assignee',
    #                     'options': {
    #                         "type": "user",
    #                         "asyncCallback": "$ctrl.getFormData",
    #                         "map": {'valueProperty': "uuid",
    #                                 'nameProperty': 'name'}
    #                     }
    #                 }
    #             ]
    #         },
    #         {
    #             'type': 'section',
    #             'htmlClass': 'col-xs-6',
    #             'items': [
    #                 'priority', {
    #                     'key': 'taskgroup',
    #                     'type': 'strapselect',
    #                     'placeholder': 'Select a Task Group',
    #                     'options': {
    #                         "type": "taskgroup",
    #                         "asyncCallback": "$ctrl.getFormData",
    #                         "map": {'valueProperty': "uuid",
    #                                 'nameProperty': 'name'}
    #                     }
    #                 }
    #             ]
    #         },
    #     ]
    # },
    TagForm,
    {
        'key': 'notes',
        "tinymceOptions": {
            "toolbar": [
                "undo redo | styleselect | bold italic | link image",
                "alignleft aligncenter alignright"
            ]
        }
    },
    {
        'type': 'fieldset',
        'items': [
            {
                'key': 'references',
                'add': 'Add Reference',
                'startEmpty': True,
                'style': {
                    'add': 'btn-success'
                },
                'items': [
                    "references[].referencetype",
                    {
                        'key': 'references[].task',
                        'type': 'strapselect',
                        'placeholder': 'Select a reference',
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
    {
        'type': 'fieldset',
        'items': [
            {
                'key': 'comments',
                'add': 'Add comment',
                'startEmpty': True,
                'style': {
                    'add': 'btn-success'
                },
                'items': [
                    "comments[]",
                ]
            }
        ]
    },
    editbuttons
]

Task = {'schema': TaskSchema, 'form': TaskForm}

"""

Schema: Task
============

Contains
--------

Task reference entry for the todo management

See also
--------

Provisions

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import editbuttons
from hfos.schemata.tag import TagData, TagForm
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

TaskSchema = base_object('task')

TaskSchema['properties'].update({
    'project': {
        'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                   'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
        'type': 'string',
        'title': 'Project which this task is part of'},
    'creator': {'type': 'string', 'title': 'Creator',
                'description': 'Creator of Task'},
    'assignee': {'type': 'string', 'title': 'Assignee',
                 'description': 'Assigned user'},
    'taskgroup': {
        'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                   'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
        'type': 'string',
        'title': 'Task group',
        'description': 'Group, this task belongs to'
    },
    'tags': TagData,
    'alert': {'type': 'string', 'title': 'Alert',
              'format': 'datetimepicker',
              'description': 'Alert time'},
    'priority': {'type': 'number', 'title': 'Priority',
                 'description': '1 is Highest priority', 'minimum': 1},
    'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
              'description': 'Entry notes'},
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
                'task': {'type': 'string', 'minLength': 36,
                         'title': 'Task UUID',
                         'description': 'Referenced Task'},
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
                'creator': {'type': 'string', 'minLength': 36,
                            'title': 'Unique Comment ID',
                            'description': 'HIDDEN'}
            }
        }
    }
})

TaskForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'name', {
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
                    {
                        'key': 'owner',
                        'type': 'strapselect',
                        'placeholder': 'Select a new Owner',
                        'options': {
                            "type": "user",
                            "asyncCallback": "$ctrl.getFormData",
                            "map": {'valueProperty': "uuid",
                                    'nameProperty': 'name'}
                        }
                    }, {
                        'key': 'assignee',
                        'type': 'strapselect',
                        'placeholder': 'Select an Assignee',
                        'options': {
                            "type": "user",
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
                    'priority', {
                        'key': 'taskgroup',
                        'type': 'strapselect',
                        'placeholder': 'Select a Task Group',
                        'options': {
                            "type": "taskgroup",
                            "asyncCallback": "$ctrl.getFormData",
                            "map": {'valueProperty': "uuid",
                                    'nameProperty': 'name'}
                        }
                    }
                ]
            },
        ]
    },
    TagForm,
    'alert',
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

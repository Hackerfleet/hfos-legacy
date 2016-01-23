"""

Schema: Task
============

Contains
--------

Task reference entry for the todo management

See also
--------

Provisions

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

TaskSchema = {
    'type': 'object',
    'id': '#task',
    'name': 'task',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36, 'title': 'Unique Task ID', 'description': 'HIDDEN'},
        'name': {'type': 'string', 'title': 'Name', 'description': 'Name of Task'},
        'project': {'type': 'string', 'title': 'Project', 'description': 'Project, the Task belongs to'},
        'creator': {'type': 'string', 'title': 'Creator', 'description': 'Creator of Task'},
        'owneruuid': {'type': 'string', 'minLength': 36, 'title': "Owner's Unique ID", 'description': 'HIDDEN'},
        'status': {
            'type': 'string', 'title': 'Task status', 'default': 'Open', 'description': 'Last status', 'enum': [
                'Open',
                'Closed',
                'Resolved',
                'In progress',
                'Duplicate',
                'Invalid',
                'Cannot reproduce',
                'Waiting',
            ]
        },
        'tags': {'type': 'string', 'title': 'Tags', 'description': 'Attached tags'},
        'priority': {'type': 'number', 'title': 'Priority', 'description': '1 is Highest priority', 'minimum': 1},
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                  'description': 'Entry notes'},
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
                    'task': {'type': 'string', 'minLength': 36, 'title': 'Task UUID',
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
                    'time': {'type': 'string', 'format': 'datetimepicker', 'title': 'Time of change',
                             'description': 'Time when this change was accepted'},
                    'change': {
                        'type': 'array',
                        'default': [],
                        'items': [

                            {'status': {'type': 'string', 'title': 'New status',
                                        'description': 'Status changed to this status'}},
                            {'comment': {'type': 'string', 'title': 'Comment', 'description': 'Comment text'}},
                            {'priority': {'type': 'number', 'title': 'Priority',
                                          'description': '1 is Highest priority'}},
                            {'tags': {'type': 'string', 'title': 'Tags', 'description': 'Attached tags'}},
                            {'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                                       'description': 'Entry notes'}},
                            {'owneruuid': {'type': 'string', 'minLength': 36, 'title': "Owner's Unique ID",
                                           'description': 'HIDDEN'}},
                            {'name': {'type': 'string', 'title': 'Name', 'description': 'Name of Task'}}
                        ]
                    },
                    'creator': {'type': 'string', 'minLength': 36, 'title': 'Unique Comment ID',
                                'description': 'HIDDEN'}
                }
            }
        }
    }
}

TaskForm = [
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
                        'type': 'uiselect',
                        'placeholder': 'Select a Project',
                        'options': {
                            "type": "project",
                            "asyncCallback": "getFormData",
                            "map": {'valueProperty': "uuid", 'nameProperty': 'name'}
                        }
                    }
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'status', 'priority'
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
                    'references[]'
                ]
            }
        ]
    },
    {
        'type': 'submit',
        'title': 'Save Task',
    }
]

Task = {'schema': TaskSchema, 'form': TaskForm}

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
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

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

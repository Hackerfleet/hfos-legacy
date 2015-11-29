"""

Schema: Project
============

Contains
--------

Project reference entry for the todo management

See also
--------

Provisions

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

Project = {
    'type': 'object',
    'id': '#Project',
    'name': 'Project',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36, 'title': 'Unique Project ID', 'description': 'HIDDEN'},
        'name': {'type': 'string', 'title': 'Name', 'description': 'Name of Project'},
        'creatoruuid': {'type': 'string', 'title': 'Creator', 'description': 'Creator of Project'},
        'owneruuid': {'type': 'string', 'minLength': 36, 'title': "Owner's Unique ID", 'description': 'HIDDEN'},
        'priority': {'type': 'number', 'title': 'Priority', 'description': '1 is Highest priority', 'minimum': 1},
        'tags': {'type': 'string', 'title': 'Tags', 'description': 'Attached tags'},
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                  'description': 'Entry notes'}
    }
}

ProjectForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'name', {
                        'key': 'owneruuid',
                        'type': 'uiselect',
                        'placeholder': 'Select an Owner',
                        'options': {
                            "type": "user",
                            "asyncCallback": "getFormData",
                            "map": {'valueProperty': "uuid", 'nameProperty': 'name'}
                        }
                    }, 'priority',
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'tags', 'creatoruuid'
                ]
            },
        ]
    },
    'notes',
    {
        'type': 'submit',
        'title': 'Save Project',
    }
]

__form__ = ProjectForm
__schema__ = Project

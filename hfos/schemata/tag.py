"""

Schema: Tag
===========

Contains
--------

Systemwide Tag definition

See also
--------

Provisions

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import editbuttons
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

# Basic Tag definitions

TagSchema = base_object('tag')
TagSchema['properties'].update({
    'color': {'type': 'string', 'format': 'color', 'title': 'Color of tag',
              'description': 'Background color of tag'},
    'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
              'description': 'Descriptive Tag notes'},
    'references': {
        'type': 'array',
        'default': [],
        'items': {
            'type': 'object',
            'properties': {
                'schema': {'type': 'string', 'minLength': 1,
                           'title': 'Schema reference',
                           'description': 'HIDDEN'},
                'uuid': {'type': 'string', 'minLength': 36,
                         'title': 'Unique ID reference',
                         'description': 'HIDDEN'}
            }
        }
    }
})

TagEditForm = [
    'name',
    'color',
    'notes',
    editbuttons
]

# Effective object tag inclusion setup

TagData = {
    'type': 'array',
    'title': 'Tags',
    'description': 'Attached tags',
    'default': [],
    'items': {
        'type': 'object',
        'properties': {
            'uuid': {
                'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-['
                           'a-fA-F0-9]{4}-['
                           'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                'type': 'string',
                'title': 'Referenced Tag'
            }
        }

    }
}

TagForm = {
    'type': 'fieldset',
    'startEmpty': True,
    'items': [
        {
            'key': 'tags',
            'add': 'Add Tag',
            'style': {
                'add': 'btn-success'
            },
            'items': [
                {
                    'key': 'tags[].uuid',
                    'type': 'strapselect',
                    'placeholder': 'Select a tag',
                    'options': {
                        "type": "tag",
                        "asyncCallback": "$ctrl.getFormData",
                        "map": {'valueProperty': "uuid",
                                'nameProperty': 'name'}
                    }
                }
            ]
        }
    ]
}

Tag = {'schema': TagSchema, 'form': TagEditForm}

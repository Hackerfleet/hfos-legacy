"""

Schema: MeshNode
============

Contains
--------

MeshNode reference entry for the mesh to set up pump start times and
durations as well as conditions..

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import savebutton

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

MeshNodeSchema = {
    'type': 'object',
    'id': '#meshnode',
    'name': 'meshnode',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36,
                 'title': 'Unique MeshNode ID', 'description': 'HIDDEN'},
        'name': {'type': 'string', 'title': 'Name',
                 'description': 'Name of MeshNode'},
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                  'description': 'Entry notes'},
        'hub': {'type': 'boolean', 'title': 'Hub node',
                'description': 'This node has data about other nodes'},
        'address': {
            'type': 'string',
            'format': 'ip-address',
            'title': 'IP Address',
            'description': 'Last known IP address of node'
        },
        'last': {
            'type': 'string', 'format': 'datetimepicker',
            'title': 'Last Seen',
            'description': 'Last date and time, this node has been seen online'
        }

    }
}

MeshNodeForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'name', 'address'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'last'
                ]
            },
        ]
    },
    'notes',
    {
        'key': 'Toggle',
        'type': 'button',
        'onClick': 'formAction("mesh", "toggle", model.uuid)',
        'title': 'Toggle MeshNode'
    },
    {
        'key': 'Suspend',
        'type': 'button',
        'condition': 'model.status',
        'onClick': 'formAction("mesh", "suspend", model.uuid)',
        'title': 'Suspend the rule for the next time'
    },
    savebutton
]

MeshNode = {'schema': MeshNodeSchema, 'form': MeshNodeForm}

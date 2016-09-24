"""

Schema: Countable
=================

Contains
--------

Generic countable thing definition

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import editbuttons

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

CountableSchema = {
    'type': 'object',
    'id': '#',
    'name': 'countable',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36,
                 'title': 'Unique Countable ID', 'description': 'HIDDEN'},
        'name': {'type': 'string', 'title': 'Name',
                 'description': 'Name of Countable'},
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                  'description': 'Entry notes'},
        'amount': {'type': 'number', 'title': 'Amount counted', 'default': 0}

    }
}

CountableForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'name', 'notes'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'amount'

                ]
            },
        ]
    },
    {
        'key': 'count',
        'type': 'button',
        'onClick': '$ctrl.formAction("countablewatcher", "count", '
                   '$ctrl.model.uuid)',
        'title': '+1'
    },
    editbuttons
]

Countable = {'schema': CountableSchema, 'form': CountableForm}

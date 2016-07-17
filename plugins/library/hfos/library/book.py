"""

Schema: Book
============

Contains
--------

Book reference entry for the library.

See also
--------

Provisions

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import editbuttons

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

BookSchema = {
    'type': 'object',
    'id': '#book',
    'name': 'book',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36, 'title': 'Unique Book ID',
                 'description': 'HIDDEN'},
        'name': {'type': 'string', 'title': 'Name',
                 'description': 'Name of Book'},
        'authors': {
            'type': 'array',
            'default': [],
            'items': {'type': 'string', 'title': 'Authors',
                      'description': 'Authors of Book'},
            'minItems': 0
        },
        'publisher': {'type': 'string', 'title': 'Publisher',
                      'description': 'Publisher of Book'},
        'owneruuid': {'type': 'string', 'minLength': 36,
                      'title': "Owner's Unique ID", 'description': 'HIDDEN'},
        'language': {'type': 'string', 'title': 'Language',
                     'description': 'Lanuage'},
        'available': {'type': 'boolean', 'title': 'Available',
                      'description': 'Eligible for lending', 'default': True},
        'status': {'type': 'string', 'title': 'Status',
                   'description': 'Last known status'},
        'statuschange': {'type': 'string', 'format': 'datetimepicker',
                         'title': 'Status date',
                         'description': 'Latest status change date'},
        'statusowner': {'type': 'string', 'minLength': 36,
                        'title': 'Unique User ID',
                        'description': 'Currently owning user'},
        'tags': {'type': 'string', 'title': 'Tags',
                 'description': 'Attached tags'},
        'isbn': {'type': 'string', 'title': 'ISBN',
                 'description': 'International Standard Book Number',
                 'pattern': '^(97(8|9))?\d{9}(\d|X)$'},
        'isbnalt': {'type': 'string', 'title': 'ISBN',
                    'description': 'Alternative International Standard Book '
                                   'Number',
                    'pattern': '^(97(8|9))?\d{9}(\d|X)$'},
        'year': {'type': 'number', 'title': 'Published',
                 'description': 'Year of publishment'},
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                  'description': 'Entry notes'},

    }
}

BookForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'name', 'year', 'available'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'publisher', 'tags', 'status'

                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'language',
                    {
                        'key': 'isbn',
                        'validationMessage': {
                            202: "Must be a numeric ISBN-10 or ISBN-13"
                        }
                    },
                    'statuschange'
                ]
            }
        ]
    },
    {
        'key': 'authors',
        'add': "Add author",
        'style': {
            'add': "btn-success"
        },
        'items': [
            'authors[]',
        ]
    },
    {
        'key': 'Lend',
        'type': 'button',
        'condition': 'model.available == true',
        'onClick': 'formAction("library", "lend", model.uuid)',
        'title': 'Lend Book'
    },
    {
        'key': 'Return',
        'type': 'button',
        'condition': 'model.available != true',
        'onClick': 'formAction("library", "return", model.uuid)',
        'title': 'Return Book'
    },
    {
        'key': 'augment',
        'type': 'button',
        'condition': 'model.isbn',
        'onClick': 'formAction("library", "augment", model.uuid)',
        'title': 'Augment Book from ISBN database'
    },
    editbuttons
]

Book = {'schema': BookSchema, 'form': BookForm}

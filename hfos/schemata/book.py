"""

Schema: Book
============

Contains
--------

Book reference entry for the library.

See also
--------

Provisions

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

Book = {
    'type': 'object',
    'id': '#Book',
    'name': 'Book',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36, 'title': 'Unique Book ID', 'description': 'HIDDEN'},
        'name': {'type': 'string', 'title': 'Name', 'description': 'Name of Book'},
        'authors': {'type': 'string', 'title': 'Authors', 'description': 'Authors of Book'},
        'owneruuid': {'type': 'string', 'minLength': 36, 'title': "Owner's Unique ID", 'description': 'HIDDEN'},
        'status': {'type': 'string', 'title': 'Book status', 'description': 'Last status'},
        'statuschange': {'type': 'string', 'format': 'date', 'title': 'Book status', 'description': 'Last status'},
        'tags': {'type': 'string', 'title': 'Tags', 'description': 'Attached tags'},
        'isbn': {'type': 'string', 'title': 'ISBN', 'description': 'International Standard Book Number',
                 'pattern': '^(97(8|9))?\d{9}(\d|X)$'},
        'year': {'type': 'number', 'title': 'Published', 'description': 'Year of publishment'},

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
                    'name', 'year', 'tags'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'status', 'authors'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'statuschange', {
                        'key': 'isbn',
                        'validationMessage': {
                            202: "Must be a numeric ISBN-10 or ISBN-13"
                        }
                    }
                ]
            }
        ]
    },
    'notes',
    {
        'type': 'submit',
        'title': 'Save Book',
    }
]

__form__ = BookForm
__schema__ = Book

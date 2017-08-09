#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2017 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "GPLv3"

"""

Schema: Book
============

Contains
--------

Book reference entry for the library.

See also
--------

Provisions


"""

from hfos.schemata.defaultform import editbuttons
from hfos.schemata.base import base_object

BookSchema = base_object('book', all_roles='crew')

BookSchema['properties'].update({
    'authors': {
        'type': 'array',
        'default': [],
        'items': {'type': 'string', 'title': 'Authors',
                  'description': 'Authors of Book'},
        'minItems': 0
    },
    'publisher': {'type': 'string', 'title': 'Publisher',
                  'description': 'Publisher of Book'},
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

})

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
        'title': 'Authors',
        'add': "Add author",
        'startEmpty': True,
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
        'onClick': '$ctrl.formAction("hfos.library.manager",'
                   '"book_lend", $ctrl.model.uuid)',
        'title': 'Lend Book'
    },
    {
        'key': 'Return',
        'type': 'button',
        'condition': 'model.available != true',
        'onClick': '$ctrl.formAction("hfos.library.manager", '
                   '"book_return", $ctrl.model.uuid)',
        'title': 'Return Book'
    },
    {
        'key': 'augment',
        'type': 'button',
        'condition': 'model.isbn',
        'onClick': '$ctrl.formAction("hfos.library.manager", '
                   '"book_augment", $ctrl.model.uuid)',
        'title': 'Augment Book from ISBN database'
    },
    editbuttons
]

Book = {'schema': BookSchema, 'form': BookForm}

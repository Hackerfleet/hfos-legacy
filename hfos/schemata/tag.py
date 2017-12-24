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

Schema: Tag
===========

Contains
--------

Systemwide Tag definition

See also
--------

Provisions


"""

from hfos.schemata.defaultform import editbuttons, lookup_field
from hfos.schemata.base import base_object, uuid_object

# Basic Tag definitions

TagSchema = base_object('tag', all_roles='crew')

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
                'uuid': uuid_object('Unique ID reference')
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
            'uuid': uuid_object('Referenced Tag')
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
                lookup_field('tags[].uuid', 'tag', 'Select a tag'),
            ]
        }
    ]
}

Tag = {'schema': TagSchema, 'form': TagEditForm}

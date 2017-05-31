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

ComponentConfigSchemaTemplate = {
    'type': 'object',
    'id': '#component',
    'name': 'component',
    'additionalproperties': True,
    'properties': {
        'uuid': {
            'type': 'string',
            'minLength': 36,
            'title': 'Unique Component ID',
            'description': 'HIDDEN',
            'readonly': True,
            'x-schema-form': {
                'condition': "false"
            }
        },
        'name': {
            'type': 'string',
            'title': 'Name',
            'description': 'Name of '
                           'Component',
            'default': 'NONAME',
            'readonly': True
        },
        'creator': {
            'type': 'string',
            'title': 'Creator',
            'description': 'Creator of Component',
            'readonly': True,
            'x-schema-form': {
                'condition': "false"
            }
        },
        'owner': {
            'type': 'string',
            'minLength': 36,
            'title': "Owner's Unique ID",
            'description': 'HIDDEN',
            'readonly': True,
            'x-schema-form': {
                'condition': "false"
            }
        },
        'color': {
            'type': 'string',  # 'format': 'color',
            'title': 'Color of component',
            'description': 'Background color of component'
        },
        'notes': {
            'type': 'string',
            'format': 'html',
            'title': 'Description',
            'description': 'Descriptive Component notes',
            'readonly': True,
            'x-schema-form': {
                'type': 'textarea',
                'fieldHtmlClass': 'textlabel'
            }
        },
        'active': {
            'type': 'boolean',
            'title': 'Active',
            'default': True
        },
        'componentclass': {
            'type': 'string',
            'title': 'Component class',
            'description': 'Type of component',
            'readonly': True
        },
    }
}

ComponentConfigForm = [
    '*'
]

ComponentBaseConfigSchema = {'schema': ComponentConfigSchemaTemplate,
                             'form': ComponentConfigForm}

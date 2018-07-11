#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2018 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""
Schema: Client
==============

Contains
--------

Client: Clientprofile to store client specific settings


"""
from hfos.schemata.defaultform import savebutton, lookup_field
from hfos.schemata.base import base_object, uuid_object, language_field
from hfos.misc import i18n as _

ScreenRotationSchema = {
    'id': '#screenrotation',
    'type': 'object',
    'properties': {
        'state': {'type': 'string', 'minLength': 1, 'title': _('New State'),
                  'description': _('State to switch to')
                  },
        'args': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'title': _('Argument Name')
                             },
                    'value': {'type': 'string', 'title': _('Argument Value')
                              }
                }
            }
        },
        'duration': {'type': 'number', 'title': _('Duration'),
                     'description': _('Timeout in seconds to swith to the next '
                                      'screen')}
    }
}

ClientconfigSchema = base_object(
    'client',
    roles_list=['crew'],
    roles_create=['crew'],
)

ClientconfigSchema['properties'].update({
    'autologin': {
        'type': 'boolean', 'title': _('Automatic login'),
        'description': _('Automatically logs in this client.')
    },
    'active': {
        'type': 'boolean', 'title': _('Active client'),
        'description': _('Indicates whether client is currently active.')
    },
    'locked': {
        'type': 'boolean', 'title': _('Locked client'),
        'description': _('Determines whether the client should be '
                         'locked against changes.')
    },
    'language': language_field(),
    'infoscreen': {
        'type': 'boolean', 'title': _('Infoscreen client'),
        'description': _('This client rotates set up infoscreens')
    },
    'currentview': {
        'type': 'string', 'minLength': 1, 'title': _('Name'),
        'description': _('Client name')
    },
    'theme': {
        'type': 'string', 'title': _('Client Theme'),
        'description': _('Theme used for user interface')
    },
    'description': {
        'type': 'string', 'format': 'html',
        'title': _('Client description'),
        'description': _('Client description')
    },
    'infoscreenrotations': {
        'type': 'array',
        'items': ScreenRotationSchema
    },
    'modules': {
        'type': 'object',
        'default': {}
    }
})

ClientconfigForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'name', 'theme', 'infoscreen'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'language', {'key': 'active', 'readonly': True}, 'locked', 'autologin'
                ]
            }
        ]
    },
    {
        'key': 'infoscreenrotations',
        'add': "Add infoscreen",
        'condition': 'model.infoscreen',
        'style': {
            'add': "btn-success"
        },
        'items': [
            'infoscreenrotations[].state',
            'infoscreenrotations[].duration',
            {
                'key': 'infoscreenrotations[].args',
                'add': 'Add argument',
                'style': {
                    'add': 'btn-success',
                },
                'items': [
                    'infoscreenrotations[].args[].name',
                    'infoscreenrotations[].args[].value'
                ]
            }
        ]
    },
    'description',
    {
        'id': 'modules',
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'help',
                'helpvalue': _('<h2>Default module configurations</h2>')
            }
        ]
    },
    savebutton
]

Client = {'schema': ClientconfigSchema, 'form': ClientconfigForm}

__schema__ = ClientconfigSchema
__form__ = ClientconfigForm

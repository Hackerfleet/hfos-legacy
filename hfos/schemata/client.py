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
from hfos.schemata.base import base_object, uuid_object

ScreenRotationSchema = {
    'id': '#screenrotation',
    'type': 'object',
    'properties': {
        'state': {'type': 'string', 'minLength': 1, 'title': 'New State',
                  'description': 'State to switch to'
                  },
        'args': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'title': 'Argument Name'
                             },
                    'value': {'type': 'string', 'title': 'Argument Value'
                              }
                }
            }
        },
        'duration': {'type': 'number', 'title': 'Duration',
                     'description': 'Timeout in seconds to swith to the next '
                                    'screen'}
    }
}

ClientconfigSchema = base_object(
    'client',
    roles_list=['crew'],
    roles_create=['crew'],
)

ClientconfigSchema['properties'].update({
    'autologin': {
        'type': 'boolean', 'title': 'Automatic login',
        'description': 'Automatically logs in this client.'
    },
    'active': {
        'type': 'boolean', 'title': 'Active client',
        'description': 'Indicates whether client is currently '
                       'active.'
    },
    'locked': {
        'type': 'boolean', 'title': 'Locked client',
        'description': 'Determines whether the client should be '
                       'locked against changes.'
    },
    'infoscreen': {
        'type': 'boolean', 'title': 'Infoscreen client',
        'description': 'This client rotates set up infoscreens'
    },
    'currentview': {
        'type': 'string', 'minLength': 1, 'title': 'Name',
        'description': 'Client name'
    },
    'theme': {
        'type': 'string', 'title': 'Client Theme',
        'description': 'Theme used for user interface'
    },
    'description': {
        'type': 'string', 'format': 'html',
        'title': 'Client description',
        'description': 'Client description'
    },
    'infoscreenrotations': {
        'type': 'array',
        'items': ScreenRotationSchema
    },
    'mapviewuuid': uuid_object('Associated Unique Mapview ID'),
    'dashboarduuid': uuid_object('Associated Unique Dashboard ID'),
    'taskgriduuid': uuid_object('Associated Unique Task Grid ID'),
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
                    {'key': 'active', 'readonly': True}, 'locked', 'autologin'
                ]
            }
        ]
    },
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            lookup_field('taskgriduuid', 'taskgridconfig',
                         html_class='col-xs-4'),
            lookup_field('dashboarduuid', 'dashboardconfig',
                         html_class='col-xs-4'),
            lookup_field('mapviewuuid', 'mapview',
                         html_class='col-xs-4'),
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
    savebutton
]

Client = {'schema': ClientconfigSchema, 'form': ClientconfigForm}

__schema__ = ClientconfigSchema
__form__ = ClientconfigForm

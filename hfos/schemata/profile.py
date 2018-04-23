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

Schema: Profile
===============

Contains
--------

Profile: Userprofile with general flags and fields


"""
from hfos.schemata.defaultform import savebutton, lookup_field
from hfos.schemata.base import base_object, uuid_object

ProfileSchema = base_object('profile', roles_create='crew')

ProfileSchema['properties'].update({
    'name': {'type': 'string', 'title': 'Name',
             'description': 'Profile name'},
    "userdata": {
        "default": {},
        "id": "#profile.userdata",
        "type": "object",
        "properties": {
            'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
                     'description': 'First name'},
            'familyname': {'type': 'string', 'minLength': 1,
                           'title': 'Family Name',
                           'description': 'Last/Family name'},
            'nick': {'type': 'string', 'title': 'nickname',
                     'description': 'Nick/calling name'},
            'location': {'type': 'string',
                         'title': 'Current user location',
                         'description': 'Autoupdated (if possible) user '
                                        'location'},
            'd-o-b': {'type': 'string', 'title': 'Birthday',
                      'format': 'datepicker',
                      'description': 'Date of birth'},
            'phone': {'type': 'string', 'title': 'Telephone number',
                      'description': 'International phone number'},
            'callsign': {'type': 'string', 'title': 'Radio callsign',
                         'description': 'HAM Radio etc callsign'},
            'shift': {'type': 'integer', 'title': 'Selected shift No.',
                      'description': '<a '
                                     'href="#/preferences/shifts">Setup '
                                     'shifts</a>'},
            'visa': {'type': 'boolean', 'title': 'Visas etc',
                     'description': 'Got all Visa documents etc?'},
            'notes': {'type': 'string', 'format': 'html',
                      'title': 'User notes',
                      'description': 'Custom user notes'},
            'image': {'type': 'string'}
        }
    },
    "components": {
        "id": "#profile.components",
        "type": "object",
        "default": {},
        "properties": {
            "enabled": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "settings": {
                "type": "array",
                "items": {
                    "id": "#components.settings",
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "settings": {"type": "object"}
                    }
                }
            }
        }
    },
    "settings": {
        "id": "#profile.settings",
        "type": "object",
        "default": {},
        "properties": {
            'color': {'type': 'string', 'title': 'User Color',
                      'format': 'color',
                      'description': 'Color used for map annotations, '
                                     'chat etc'},
            'theme': {'type': 'string', 'title': 'User Theme',
                      'description': 'Theme used for user interface'},
            'background': {'type': 'string',
                           'title': 'Background Image',
                           'description': 'Application background image',
                           'default': 'default'},
            'notifications': {
                "id": "#profile.settings.notifications",
                "type": "object",
                "properties": {
                    'delete': {'type': 'boolean', 'title': 'Delete '
                                                           'confirmation',
                               'description': 'Enable confirmation '
                                              'warning on object '
                                              'deletion.',
                               'default': True}
                }
            },
            'notes': {'type': 'string', 'format': 'html',
                      'title': 'Profile notes',
                      'description': 'Custom profile notes'},
            'menu': {
                "type": "array",
                "items": {
                    "id": "menuentry",
                    "title": "Menu entry",
                    "type": "object",
                    "properties": {
                        "title": {"type": "string",
                                  "title": "Menuitem title"},
                        "row": {"type": "integer",
                                "title": "Menuitem row"},
                        "col": {"type": "integer",
                                "title": "Menuitem column"},
                        "size": {"type": "integer",
                                 "title": "Menuitem size"},
                    }
                }
            },
            'mapviewuuid': uuid_object('Default Unique Mapview ID'),
            'taskgriduuid': uuid_object('Default Unique Taskgrid ID'),
            'dashboarduuid': uuid_object('Default Unique Dashboard ID')
        }
    },
    "alertconfig": {
        "id": "#profile.alertconfig",
        "type": "object",
        "default": {},
        "properties": {
            'ontime': {'type': 'string', 'title': 'Active',
                       'description': 'Active alert times'}

        }
    }

})

ProfileForm = [
    'name',
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'help',
                'helpvalue': '<h2>User information</h2>'
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'userdata.name', 'userdata.d-o-b', 'userdata.shift'
                ]
            }, {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'userdata.familyname', 'userdata.callsign',
                    'userdata.location'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'userdata.nick', 'userdata.phone', 'userdata.visa'
                ]
            }
        ]
    },
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'help',
                'helpvalue': '<h2>User interface settings</h2>'
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-3',
                'items': [
                    'settings.color', 'settings.theme'
                ]
            }, {
                'type': 'section',
                'htmlClass': 'col-xs-9',
                'items': [
                    'settings.background'
                ]
            }
        ]
    },
    'settings.notifications',
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'help',
                'helpvalue': '<h2>Default module configurations</h2>'
            },
            lookup_field('settings.dashboarduuid', 'dashboardconfig', 'Select a Dashboard', 'col-xs-4'),
            lookup_field('settings.taskgriduuid', 'taskgridconfig', 'Select a Dashboard', 'col-xs-4'),
            lookup_field('settings.mapviewuuid', 'mapview', 'Select a Dashboard', 'col-xs-4'),
        ],
    },
    #'alertconfig',
    'userdata.notes',
    savebutton
]

Profile = {'schema': ProfileSchema, 'form': ProfileForm}

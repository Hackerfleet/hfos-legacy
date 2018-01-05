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
Schema: System
==============

Contains
--------

System: Global systemwide settings


"""
from hfos.schemata.defaultform import savebutton, lookup_field
from hfos.schemata.base import base_object, uuid_object

SystemconfigSchema = base_object('systemconfig')

SystemconfigSchema['properties'].update({
    'active': {
        'type': 'boolean', 'title': 'Active configuration',
        'description': 'Determines which configuration will be used. '
                       'Only one can be active.',
        'default': False
    },
    'salt': {
        'type': 'string', 'minLength': 1, 'title': 'Salt',
        'description': 'System hashing salt'
    },
    'description': {
        'type': 'string', 'format': 'html',
        'title': 'Description',
        'description': 'System description'
    },
    'allowregister': {
        'type': 'boolean', 'title': 'Registration open',
        'description': 'Allow self registration of new users'
    },
    'vesseluuid': uuid_object('Associated Vessel Unique ID'),
    'defaultmapviewuuid': uuid_object('Default Mapview Unique ID'),
    'defaultdashboarduuid': uuid_object('Default Dashboard Unique ID'),
    'defaulttaskgriduuid': uuid_object('Default Taskgrid Unique ID'),
    'defaulttheme': {'type': 'string', 'title': 'Default new client theme',
                     'description': 'Default theme used for user '
                                    'interface'},
    'hostname': {'type': 'string', 'title': 'Public hostname',
                 'description': 'Public FQDN hostname to use for internet '
                                'based services (host.domain.tld)'}
})

SystemconfigForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'name'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    {'key': 'active', 'readonly': True}, 'allowregister'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    lookup_field('defaultmapviewuuid', 'mapview'),
                    lookup_field('defaultdashboarduuid', 'dashboardconfig'),
                    lookup_field('defaulttaskgriduuid', 'taskgridconfig')
                ]
            }
        ]
    },

    'description',
    savebutton
]

SystemconfigOptions = {
    'hidden': ['salt']
}

Systemconfig = {'schema': SystemconfigSchema, 'form': SystemconfigForm,
                'options': SystemconfigOptions}

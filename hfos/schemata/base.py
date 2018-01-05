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
from hfos.schemata.defaultform import lookup_field

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""

Schema: Base
============

Basic HFOS object schema utilities

Contains
--------

uuid_object: For inserting UUID fields
base_object: For generating a basic HFOS object schema


"""


def uuid_object(title="Reference", description="Select an object", display=True):
    """Generates a regular expression controlled UUID field"""

    uuid = {
        'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{'
                   '4}-['
                   'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
        'type': 'string',
        'title': title,
        'description': description
    }

    if not display:
        uuid['x-schema-form'] = {
            'condition': "false"
        }

    return uuid


def base_object(name,
                no_perms=False,
                has_owner=True,
                has_uuid=True,
                roles_write=None,
                roles_read=None,
                roles_list=None,
                roles_create=None,
                all_roles=None):
    """Generates a basic object with RBAC properties"""
    base_schema = {
        'id': '#' + name,
        'type': 'object',
        'name': name,
        'properties': {}
    }

    if not no_perms:
        if all_roles:
            roles_create = ['admin', all_roles]
            roles_write = ['admin', all_roles]
            roles_read = ['admin', all_roles]
            roles_list = ['admin', all_roles]
        else:
            if roles_write is None:
                roles_write = ['admin']
            if roles_read is None:
                roles_read = ['admin']
            if roles_list is None:
                roles_list = ['admin']
            if roles_create is None:
                roles_create = ['admin']

        if isinstance(roles_create, str):
            roles_create = [roles_create]
        if isinstance(roles_write, str):
            roles_write = [roles_write]
        if isinstance(roles_read, str):
            roles_read = [roles_read]
        if isinstance(roles_list, str):
            roles_list = [roles_list]

        if has_owner:
            roles_write.append('owner')
            roles_read.append('owner')
            roles_list.append('owner')

        base_schema['roles_create'] = roles_create
        base_schema['properties'].update({
            'perms': {
                'id': '#perms',
                'type': 'object',
                'name': 'perms',
                'properties': {
                    'write': {
                        'type': 'array',
                        'default': roles_write,
                        'items': {
                            'type': 'string',
                        }
                    },
                    'read': {
                        'type': 'array',
                        'default': roles_read,
                        'items': {
                            'type': 'string',
                        }
                    },
                    'list': {
                        'type': 'array',
                        'default': roles_list,
                        'items': {
                            'type': 'string',
                        }
                    }
                },
                'default': {},
                'x-schema-form': {
                    'condition': "false"
                }
            },
            'name': {
                'type': 'string'
            }
        })

        if has_owner:
            # TODO: Schema should allow specification of non-local owners as
            #  well
            # as special accounts like admin or even system perhaps
            # base_schema['required'] = base_schema.get('required', [])
            # base_schema['required'].append('owner')
            base_schema['properties'].update({
                'owner': uuid_object(title='Unique Owner ID', display=False)
            })

    # TODO: Using this causes all sorts of (obvious) problems with the object
    # manager
    if has_uuid:
        base_schema['properties'].update({
            'uuid': uuid_object(title='Unique ' + name + ' ID', display=False)
        })
        base_schema['required'] = ["uuid"]

    return base_schema

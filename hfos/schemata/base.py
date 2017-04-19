"""

Schema: User
============

Account credentials and administrativa

Contains
--------

User: Useraccount object

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""
from hfos.schemata.defaultform import noform

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


def base_object(name,
                has_owner=True,
                has_uuid=True,
                roles_write=None,
                roles_read=None,
                roles_list=None,
                roles_create=None):

    if roles_write is None:
        roles_write = ['admin']
        if has_owner:
            roles_write.append('owner')
    if roles_read is None:
        roles_read = ['admin']
        if has_owner:
            roles_read.append('owner')
    if roles_list is None:
        roles_list = ['admin']
        if has_owner:
            roles_list.append('owner')
    if roles_create is None:
        roles_create = ['admin']
        
    base_schema = {
        'id': '#' + name,
        'type': 'object',
        'name': name,
        'roles_create': roles_create,
        'properties': {
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
                'default': {}
            },
            'name': {
                'type': 'string'
            },
        },
    }

    if has_uuid:
        base_schema['properties'].update({
            'uuid': {
                'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                           'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                'type': 'string',
                'title': 'Unique ' + name + ' ID',
            }
        })
        base_schema['required'] = ["uuid"]

    if has_owner:
        base_schema['properties'].update({
            'owner': {
                'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                           'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                'type': 'string',
                'title': 'Unique Owner ID'
            }
        })
        # TODO: Schema should allow specification of non-local owners as well
        # as special accounts like admin or even system perhaps
        # base_schema['required'] = base_schema.get('required', [])
        # base_schema['required'].append('owner')

    return base_schema
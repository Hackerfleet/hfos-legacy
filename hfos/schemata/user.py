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
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

UserSchema = base_object('user', roles_list=['owner', 'admin', 'crew'])

UserSchema['properties'].update({
    'passhash': {
        'type': 'string'
    },
    'roles': {
        'type': 'array',
        'items': {
            'type': 'string'
        },
        'default': ['crew']
    }

})

UserOptions = {
    'hidden': ['passhash', 'roles']
}

User = {'schema': UserSchema, 'form': noform, 'options': UserOptions}

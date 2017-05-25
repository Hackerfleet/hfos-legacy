"""

Provisioning: User
==================

Contains
--------

Just creates a fulltext searchable index over the username field.

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.provisions.base import provisionList
from hfos.database import objectmodels
from hfos.logger import hfoslog, warn

from uuid import uuid4

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

Users = [{
    'name': 'System',
    'uuid': str(uuid4()),
    'roles': ['admin', 'system', 'crew']
}]


def provision(**kwargs):
    # TODO: Add a root user and make sure owner can access it later.
    # Setting up details and asking for a password here is not very useful,
    # since this process is usually run automated.

    if kwargs.get('overwrite', False):
        hfoslog('Refusing to overwrite system user!', lvl=warn,
                emitter='PROVISIONS')
        kwargs['overwrite'] = False

    system_user_count = objectmodels['user'].count({'name': 'System'})
    if system_user_count == 0 or kwargs.get('clear', False):
        provisionList(Users, objectmodels['user'], **kwargs)
        hfoslog('Provisioning: Users: Done.', emitter="PROVISIONS")
    else:
        hfoslog('System user already present.', lvl=warn, emitter='PROVISIONS')

if __name__ == "__main__":
    provision()

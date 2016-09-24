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
from hfos.logger import hfoslog

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

Users = [
]


def provision():
    # TODO: Add a root user and make sure owner can access it later.
    # Setting up details and asking for a password here is not very useful, since this process is usually run automated.

    provisionList(Users, objectmodels['user'], indexes=['name'], clear=False)
    hfoslog('Provisioning: Users: Done.', emitter="PROVISIONS")


if __name__ == "__main__":
    provision()

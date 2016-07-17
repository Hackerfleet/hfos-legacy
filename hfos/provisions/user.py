"""

Provisioning: User
==================

Contains
--------

Just creates a fulltext searchable index over the username field.

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.provisions.base import provisionList
from hfos.database import userobject
from hfos.logger import hfoslog

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

Users = [
]


def provision():
    provisionList(Users, userobject, indexes=['name'], clear=True)
    hfoslog('Provisioning: Users: Done.', emitter="PROVISIONS")


if __name__ == "__main__":
    provision()

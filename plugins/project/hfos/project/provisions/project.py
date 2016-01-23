"""

Provisioning: Project
=====================

Contains
--------

Just creates a fulltext searchable index over the name field.

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from hfos.provisions.base import provisionList
from hfos.database import projectobject
from hfos.logger import hfoslog

Projects = [
]


def provision():
    provisionList(Projects, projectobject, indexes=['name'], clear=True)
    hfoslog('[PROV] Provisioning: Project: Done.')


if __name__ == "__main__":
    provision()

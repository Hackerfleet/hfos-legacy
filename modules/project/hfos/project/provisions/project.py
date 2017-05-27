"""

Provisioning: Project
=====================

Contains
--------

Just creates a fulltext searchable index over the name field.

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.provisions.base import provisionList
from hfos.database import projectobject
from hfos.logger import hfoslog

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

Projects = [
]


def provision(**kwargs):
    provisionList(Projects, projectobject, indices=['name'], **kwargs)
    hfoslog('[PROV] Provisioning: Project: Done.')


if __name__ == "__main__":
    provision()

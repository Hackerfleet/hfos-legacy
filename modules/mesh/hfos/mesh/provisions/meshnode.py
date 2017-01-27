"""

Provisioning: Meshnodes
=======================

Contains
--------

Predefined open layers.

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.provisions.base import provisionList
from hfos.database import objectmodels
from hfos.logger import hfoslog

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

meshnodes = [
    {
        "name": "Primary Hackerfleet Hub",
        "uuid": "2647d353-46c7-4ec7-a73d-9255da9162ef",
        "hub": True,
        "address": "hfos.hackerfleet.de",
        "notes": "The first community operated (primary) node hub, located "
                 "in Germany."
    }
]


def provision():
    provisionList(meshnodes, objectmodels['meshnode'], overwrite=True,
                  clear=False)
    hfoslog('Provisioning: Meshnodes: Done.', emitter='PROVISIONS')


if __name__ == "__main__":
    provision()

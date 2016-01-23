"""

Provisioning: Mapview
==================

Contains
--------

Mapview skeleton for ships

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from hfos.provisions.base import provisionList
from hfos.database import mapviewobject
from hfos.logger import hfoslog

Mapviews = [
    {'name': 'Empty Mapview',
     'uuid': 'b69104cf-8ee7-4c81-aeca-dde272d67b63',
     'notes': 'Default empty mapview.'
     }
]


def provision():
    provisionList(Mapviews, mapviewobject, indexes=['name'], clear=True)
    hfoslog('[PROV] Provisioning: Mapviews: Done.')


if __name__ == "__main__":
    provision()

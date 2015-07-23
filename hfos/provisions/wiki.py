"""

Provisioning: Wiki
==================

Contains
--------

Wiki skeleton for ships

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from hfos.provisions.base import provisionList
from hfos.database import wikipageobject
from hfos.logger import hfoslog

WikiPages = [
    {'name': 'equipment',
     'title': 'Vessel Equipment List',
     'text': 'Predefined testing page'
     }
]

if __name__ == "__main__":
    provisionList(WikiPages, wikipageobject)
    hfoslog('[PROV] Provisioning: WikiPages: Done.')

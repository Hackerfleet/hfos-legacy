"""

Provisioning: Wiki
==================

Contains
--------

Wiki skeleton for ships

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.provisions.base import provisionList
from hfos.database import wikipageobject
from hfos.logger import hfoslog

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

WikiPages = [
    {'name': 'Index',
     'uuid': '8cc76c46-7488-4a0d-8ab9-1ca7c17f1b75',
     'title': 'Page Index',
     'text': 'No Index has been generated yet. This usually means, no pages '
             'exist.'
     }
]


def provision():
    provisionList(WikiPages, wikipageobject)
    hfoslog('[PROV] Provisioning: WikiPages: Done.')


if __name__ == "__main__":
    provision()

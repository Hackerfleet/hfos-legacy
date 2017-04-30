"""

Provisioning: Automats
========================

Contains
--------

Automats for ships

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.provisions.base import provisionList
from hfos.database import objectmodels
from hfos.logger import hfoslog

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

Automats = [
    {
        'name': 'Default',
        'uuid': '7df83542-c1c1-4c70-b754-51174a53453a',
        'description': 'Default blank automat',
        'shared': True,
        'locked': False,
        'cards': []
    }
]


def provision(*args):
    provisionList(Automats, objectmodels['automatconfig'], clear=clear)
    hfoslog('[PROV] Provisioning: Automats: Done.')

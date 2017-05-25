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

Automata = [
    {
        'name': 'Default',
        'uuid': '7df83542-c1c1-4c70-b754-51174a53453a',
        'description': 'Default blank automat',
        'shared': True,
        'locked': False
    }
]


def provision(*args, **kwargs):
    provisionList(Automata, objectmodels['automatrule'], **kwargs)
    hfoslog('[PROV] Provisioning: Automata: Done.')

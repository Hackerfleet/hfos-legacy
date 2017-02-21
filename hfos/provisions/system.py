"""
Schema: System
==============

Contains
--------

System: Global systemwide settings

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.provisions.base import provisionList
from hfos.database import objectmodels, makesalt
from hfos.logger import hfoslog
from uuid import uuid4
from random import randint

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

systemconfig = {
    'uuid': str(uuid4()),
    'allowregister': True,
    'salt': makesalt(),
    'active': True,
    'name': 'Default System Configuration',
    'description': 'Default System description'
}


def provision():
    currentconfig = objectmodels['systemconfig'].find_one({'active': True})

    if currentconfig is None:
        provisionList([systemconfig], objectmodels['systemconfig'])
        hfoslog('Provisioning: System: Done.', emitter='PROVISIONS')
    else:
        from pprint import pprint
        pprint(currentconfig)
        hfoslog(
            'NOT provisioning system configuration, as there is an active '
            'configuration in the database.\n'
            'Please manually delete the mongo collection, until an override '
            'has been implemented.')

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


def provision(*args):
    provisionList([systemconfig], objectmodels['systemconfig'], *args)
    hfoslog('Provisioning: System: Done.', emitter='PROVISIONS')

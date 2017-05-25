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
from hfos.logger import hfoslog, warn
from uuid import uuid4

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

systemconfig = {
    'uuid': str(uuid4()),
    'allowregister': True,
    'salt': makesalt(),
    'active': True,
    'name': 'Default System Configuration',
    'description': 'Default System description'
}


def provision(*args, **kwargs):
    clear = kwargs.get('clear', False)
    overwrite = kwargs.get('overwrite', False)

    default_system_config_count = objectmodels['systemconfig'].count({
        'name': 'Default System Configuration'})

    if default_system_config_count == 0 or (clear or overwrite):
        provisionList([systemconfig], objectmodels['systemconfig'], *args,
                      **kwargs)
        hfoslog('Provisioning: System: Done.', emitter='PROVISIONS')
    else:
        hfoslog('Default system configuration already present.', lvl=warn,
                emitter='PROVISIONS')

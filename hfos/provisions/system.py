#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2017 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "GPLv3"

"""
Schema: System
==============

Contains
--------

System: Global systemwide settings


"""

from hfos.provisions.base import provisionList
from hfos.database import objectmodels, makesalt
from hfos.logger import hfoslog, warn
from uuid import uuid4

systemconfig = {
    'uuid': str(uuid4()),
    'allowregister': True,
    'salt': makesalt(),
    'active': True,
    'name': 'Default System Configuration',
    'description': 'Default System description'
}


def provision(*args, **kwargs):
    """Provision a basic system configuration"""

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

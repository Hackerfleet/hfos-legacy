#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2018 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""
Schema: System
==============

Contains
--------

System: Global systemwide settings


"""

from hfos.misc import std_salt
from hfos.logger import hfoslog, warn
from uuid import uuid4

SystemConfiguration = {
    'uuid': str(uuid4()),
    'salt': std_salt(),
    'active': True,
    'name': 'Default System Configuration',
    'description': 'Default System description',
    'hostname': 'localhost'
}


def provision_system_config(items, database_name, overwrite=False, clear=False, skip_user_check=False):
    """Provision a basic system configuration"""

    from hfos.provisions.base import provisionList
    from hfos.database import objectmodels

    default_system_config_count = objectmodels['systemconfig'].count({
        'name': 'Default System Configuration'})

    if default_system_config_count == 0 or (clear or overwrite):
        provisionList([SystemConfiguration], 'systemconfig', overwrite, clear, skip_user_check)
        hfoslog('Provisioning: System: Done.', emitter='PROVISIONS')
    else:
        hfoslog('Default system configuration already present.', lvl=warn,
                emitter='PROVISIONS')


provision = {'data': SystemConfiguration, 'method': provision_system_config, 'dependencies': 'user'}

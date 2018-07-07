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

from hfos.logger import hfoslog
from uuid import uuid4

SystemVessel = {
    'name': 'Default System Vessel',
    'uuid': str(uuid4()),
}


def provision_system_vessel(items, database_name, overwrite=False, clear=False, skip_user_check=False):
    """Provisions the default system vessel"""

    from hfos.provisions.base import provisionList
    from hfos.database import objectmodels

    vessel = objectmodels['vessel'].find_one({'name': 'Default System Vessel'})
    if vessel is not None:
        if overwrite is False:
            hfoslog('Default vessel already existing. Skipping provisions.')
            return
        else:
            vessel.delete()

    provisionList([SystemVessel], 'vessel', overwrite, clear, skip_user_check)

    sysconfig = objectmodels['systemconfig'].find_one({'active': True})
    hfoslog('Adapting system config for default vessel:', sysconfig)
    sysconfig.vesseluuid = SystemVessel['uuid']
    sysconfig.save()

    hfoslog('Provisioning: Vessel: Done.', emitter='PROVISIONS')


provision = {'data': SystemVessel, 'method': provision_system_vessel, 'dependencies': 'system'}

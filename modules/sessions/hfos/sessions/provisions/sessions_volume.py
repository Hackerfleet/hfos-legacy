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

Provisioning: Volume
====================

Contains
--------

Predefined volumes


"""

from hfos.provisions.base import provisionList
from hfos.database import objectmodels, instance
from hfos.logger import hfoslog
from os.path import join

Volumes = [
    {
        'name': 'hfos.sessions',
        'uuid': 'f47711bf-51d0-49ed-aacb-68783ce16a2b',
        'description': 'Session attachment storage',
        'path': join('/var/lib/hfos/', instance, 'volumes/sessions'),
        'flags': ['uservolume'],
        'perms': {
            'read': ['admin', 'chair'],
            'write': ['admin', 'chair'],
            'list': ['admin', 'chair']
        },
        'default_permissions': {
            'read': ['admin', 'owner', 'chair'],
            'write': ['admin', 'owner', 'chair', 'crew'],
            'list': ['admin', 'chair']
        }
    }
]


def provision(*args, **kwargs):
    provisionList(Volumes, objectmodels['volume'], **kwargs)
    hfoslog('[PROV] Provisioning: Volumes: Done.')

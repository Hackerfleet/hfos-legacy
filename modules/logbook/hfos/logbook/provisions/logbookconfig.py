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

Provisioning: Logbooks
========================

Contains
--------

Logbooks for ships


"""

from hfos.provisions.base import provisionList
from hfos.database import objectmodels
from hfos.logger import hfoslog

Logbooks = [
    {
        'name': 'Default',
        'uuid': '7df83542-c1c1-4c70-b754-51174a53453a',
        'description': 'Default blank logbook',
        'shared': True,
        'locked': False,
    }
]


def provision(**kwargs):
    provisionList(Logbooks, objectmodels['logbookconfig'], **kwargs)
    hfoslog('[PROV] Provisioning: Logbooks: Done.')

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

Provisioning: Meshnodes
=======================

Contains
--------

Predefined open layers.


"""

from hfos.provisions.base import provisionList
from hfos.database import objectmodels
from hfos.logger import hfoslog

meshnodes = [
    {
        "name": "Primary Hackerfleet Hub",
        "uuid": "2647d353-46c7-4ec7-a73d-9255da9162ef",
        "hub": True,
        "address": "hfos.hackerfleet.de",
        "notes": "The first community operated (primary) node hub, located "
                 "in Germany."
    }
]


def provision(**kwargs):
    provisionList(meshnodes, objectmodels['meshnode'], **kwargs)
    hfoslog('Provisioning: Meshnodes: Done.', emitter='PROVISIONS')


if __name__ == "__main__":
    provision()

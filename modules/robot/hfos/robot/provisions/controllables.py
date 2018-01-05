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

Provisioning: Controllables
===========================

Contains
--------

Controllables for several predefined functions.


"""

from hfos.provisions.base import provisionList
from hfos.database import controllableobject
from hfos.logger import hfoslog

Controllables = [
    {
        "uuid": "51358884-0d61-40a7-acd6-e1f35bbfa3c8",
        "name": "engine_power",
        "description": "Engine power setting",
        "type": "analog",
        "min": 0,
        "max": 255
    },
    {
        "uuid": "23cd1b85-e7b5-4c70-a072-8bca5ede4d92",
        "name": "engine_reverse",
        "description": "Engine reverse setting",
        "type": "digital",
        "min": 0,
        "max": 255
    },
    {
        "uuid": "9c4bccbf-17b0-4c8f-bceb-143006287cf7",
        "name": "rudder",
        "description": "Rudder setting",
        "type": "analog",
        "min": 0,
        "center": 127,
        "max": 255
    },
    {
        "uuid": "3136b068-06f5-48e3-9735-cfe77aff0517",
        "name": "light_stb",
        "description": "Light Starboard",
        "type": "digital",
        "min": 0,
        "max": 255
    },
    {
        "uuid": "18b74670-f069-4ff4-b0e3-7bf812f5fc0e",
        "name": "light_pt",
        "description": "Light Port",
        "type": "digital",
        "min": 0,
        "max": 255
    },
    {
        "uuid": "92968d37-e4a7-4088-b9e8-59787ad0b983",
        "name": "pump_on",
        "description": "Activate coolant pump",
        "type": "digital",
        "min": 0,
        "max": 255
    },
    {
        "uuid": "c85e391d-2586-4157-b386-6b583d5d1934",
        "name": "pump_off",
        "description": "Deactivate coolant pump",
        "type": "digital",
        "min": 0,
        "max": 255
    },
]


def provision(**kwargs):
    provisionList(Controllables, controllableobject, **kwargs)
    hfoslog('[PROV] Provisioning: Controllables: Done.')


if __name__ == "__main__":
    provision()

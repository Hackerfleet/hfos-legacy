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

Provisioning: Nodestates
========================

Contains
--------

NodeStates for various vessel types. 
Choose a provision that matches your vessel. 


"""

# TODO: Allow choosing of predefined provisions.

from hfos.provisions.base import provisionList
from hfos.database import objectmodels
from hfos.logger import hfoslog

NodeStates = [
    {
        "label-activated": "Online",
        "position": {
            "y": 6,
            "x": 0
        },
        "active": False,
        "excluded": [],
        "color": "rgb(175, 48, 48)",
        "name": "Offline",
        "uuid": "d77db9e8-4e59-47d9-9594-2c797610ad5e",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-wifi",
        "untrigger": [
            "b3949e02-4d4e-4765-a9aa-6a0bd3a6318d",
            "62b69316-7560-4333-b774-cdfd435c0428",
            "4e538440-5c1b-4fc8-a69f-a6090fbfefa7"
        ],
        "group": "network"
    },
    {
        "label-activated": "Offline",
        "position": {
            "y": 6,
            "x": 2
        },
        "active": False,
        "excluded": [
            "d77db9e8-4e59-47d9-9594-2c797610ad5e"
        ],
        "color": "rgb(159, 106, 38)",
        "name": "Online 2G",
        "uuid": "b3949e02-4d4e-4765-a9aa-6a0bd3a6318d",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-wifi",
        "untrigger": [
            "d77db9e8-4e59-47d9-9594-2c797610ad5e"
        ],
        "group": "network"
    },
    {
        "label-activated": "Offline",
        "position": {
            "y": 6,
            "x": 4
        },
        "active": False,
        "untrigger": [
            "d77db9e8-4e59-47d9-9594-2c797610ad5e"
        ],
        "color": "rgb(189, 195, 47)",
        "name": "Online 3G",
        "uuid": "62b69316-7560-4333-b774-cdfd435c0428",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-wifi",
        "excluded": [
            "d77db9e8-4e59-47d9-9594-2c797610ad5e"
        ],
        "group": "network"
    },
    {
        "label-activated": "Offline",
        "position": {
            "y": 6,
            "x": 6
        },
        "active": False,
        "untrigger": [
            "d77db9e8-4e59-47d9-9594-2c797610ad5e"
        ],
        "color": "rgb(60, 184, 53)",
        "name": "Online 4G",
        "uuid": "4e538440-5c1b-4fc8-a69f-a6090fbfefa7",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-wifi",
        "excluded": [
            "d77db9e8-4e59-47d9-9594-2c797610ad5e"
        ],
        "group": "network"
    },
    {
        "label-activated": "Pull Anchor",
        "position": {
            "y": 9,
            "x": 2
        },
        "active": False,
        "excluded": [],
        "color": "rgb(0, 118, 209)",
        "name": "Anchoring",
        "uuid": "121d5144-9ce0-499f-9378-556efdb6b451",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-anchor",
        "untrigger": [
            "44c060b0-6002-4a40-9e88-6266918a813a",
            "002c18fd-e229-445b-a936-0de9ad39766d",
            "5b75df66-880f-4afb-9bb6-c26d2be35869",
            "6c5564ea-ce11-4d56-a2e2-28dfdcb40a11",
            "840b8152-47e2-453b-a5b3-26681a966aea"
        ],
        "group": "nautical"
    },
    {
        "label-activated": "Detach",
        "position": {
            "y": 9,
            "x": 4
        },
        "active": False,
        "excluded": [],
        "color": "rgb(51, 125, 170)",
        "name": "Moored",
        "uuid": "950a853b-a833-4eb0-a628-08a4273ae0e0",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-anchor",
        "untrigger": [
            "44c060b0-6002-4a40-9e88-6266918a813a",
            "002c18fd-e229-445b-a936-0de9ad39766d",
            "5b75df66-880f-4afb-9bb6-c26d2be35869",
            "6c5564ea-ce11-4d56-a2e2-28dfdcb40a11",
            "840b8152-47e2-453b-a5b3-26681a966aea"
        ],
        "group": "nautical"
    },
    {
        "label-activated": "Under control",
        "position": {
            "y": 9,
            "x": 6
        },
        "active": False,
        "untrigger": [
            "121d5144-9ce0-499f-9378-556efdb6b451",
            "950a853b-a833-4eb0-a628-08a4273ae0e0"
        ],
        "color": "rgb(174, 47, 47)",
        "name": "Adrift",
        "uuid": "44c060b0-6002-4a40-9e88-6266918a813a",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-exclamation-circle",
        "excluded": [],
        "group": "nautical"
    },
    {
        "label-activated": "Engine stopped",
        "position": {
            "y": 0,
            "x": 4
        },
        "active": False,
        "excluded": [],
        "color": "rgb(57, 170, 63)",
        "name": "Underway (Engine)",
        "uuid": "002c18fd-e229-445b-a936-0de9ad39766d",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-ship",
        "untrigger": [
            "44c060b0-6002-4a40-9e88-6266918a813a",
            "950a853b-a833-4eb0-a628-08a4273ae0e0",
            "121d5144-9ce0-499f-9378-556efdb6b451"
        ],
        "group": "nautical"
    },
    {
        "label-activated": "Unrig",
        "position": {
            "y": 0,
            "x": 6
        },
        "active": False,
        "excluded": [],
        "color": "rgb(66, 177, 83)",
        "name": "Underway (Sails)",
        "uuid": "5b75df66-880f-4afb-9bb6-c26d2be35869",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-ship",
        "untrigger": [
            "44c060b0-6002-4a40-9e88-6266918a813a",
            "121d5144-9ce0-499f-9378-556efdb6b451",
            "950a853b-a833-4eb0-a628-08a4273ae0e0"
        ],
        "group": "nautical"
    },
    {
        "label-activated": "Stop",
        "position": {
            "y": 0,
            "x": 2
        },
        "active": False,
        "excluded": [],
        "color": "rgb(77, 168, 72)",
        "name": "Underway (Littoral)",
        "uuid": "6c5564ea-ce11-4d56-a2e2-28dfdcb40a11",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-ship",
        "untrigger": [
            "121d5144-9ce0-499f-9378-556efdb6b451",
            "950a853b-a833-4eb0-a628-08a4273ae0e0",
            "840b8152-47e2-453b-a5b3-26681a966aea"
        ],
        "group": "nautical"
    },
    {
        "label-activated": "Calmed down",
        "position": {
            "y": 12,
            "x": 0
        },
        "group": "nautical",
        "active": False,
        "untrigger": [],
        "color": "rgb(168, 49, 49)",
        "name": "Heavy Conditions",
        "uuid": "b2e34d04-c113-4fa5-9116-efeae76be4bf",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-ship",
        "excluded": []
    },
    {
        "label-activated": "Unplug",
        "position": {
            "y": 3,
            "x": 6
        },
        "active": False,
        "excluded": [],
        "color": "rgb(75, 174, 69)",
        "name": "Land Power",
        "uuid": "44a3d794-ca7f-43dd-b7ac-dd42bb362773",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-plug",
        "untrigger": [],
        "group": "power"
    },
    {
        "label-activated": "Stop Generator",
        "position": {
            "y": 3,
            "x": 4
        },
        "active": False,
        "excluded": [],
        "color": "rgb(175, 186, 67)",
        "name": "Generator",
        "uuid": "08a15567-a21e-49d3-b1c3-028b8c7a6eb7",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-bolt",
        "untrigger": [],
        "group": "power"
    },
    {
        "label-activated": "Disable Battery",
        "position": {
            "y": 3,
            "x": 2
        },
        "active": False,
        "untrigger": [
            "44a3d794-ca7f-43dd-b7ac-dd42bb362773"
        ],
        "color": "rgb(226, 158, 50)",
        "name": "Battery Power",
        "uuid": "9df160d0-2853-45eb-801f-d82f8c1ced6f",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-battery",
        "excluded": [
            "44a3d794-ca7f-43dd-b7ac-dd42bb362773",
            "08a15567-a21e-49d3-b1c3-028b8c7a6eb7"
        ],
        "group": "power"
    },
    {
        "label-activated": "Recharged",
        "position": {
            "y": 3,
            "x": 0
        },
        "active": False,
        "excluded": [],
        "color": "rgb(242, 41, 41)",
        "name": "Short on power",
        "uuid": "1b7e659b-18b1-4215-9252-e05a1652f63d",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-battery-quarter",
        "untrigger": [],
        "group": "power"
    },
    {
        "label-activated": "Gone littoral",
        "position": {
            "y": 0,
            "x": 0
        },
        "active": False,
        "excluded": [
            "121d5144-9ce0-499f-9378-556efdb6b451"
        ],
        "color": "rgb(57, 91, 154)",
        "name": "Underway (Offshore)",
        "uuid": "840b8152-47e2-453b-a5b3-26681a966aea",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-ship",
        "untrigger": [
            "6c5564ea-ce11-4d56-a2e2-28dfdcb40a11",
            "950a853b-a833-4eb0-a628-08a4273ae0e0"
        ],
        "group": "nautical"
    },
    {
        "label-activated": "Internet",
        "position": {
            "y": 9,
            "x": 0
        },
        "group": "network",
        "active": False,
        "untrigger": [],
        "color": "rgb(10, 198, 0)",
        "name": "Connectivity",
        "uuid": "6d650454-e9b1-40ca-94a6-be817deb5448",
        "size": {
            "height": 2,
            "width": 3
        },
        "icon": "fa-globe",
        "readonly": True,
        "excluded": []
    }
]


def default_provision(**kwargs):
    provisionList(NodeStates, objectmodels['nodestate'], **kwargs)
    hfoslog('[PROV] Provisioning: Nodestates: Done.')

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

Provisioning: Taskgrid
======================

Contains
--------

Two default taskgrids with the provisioned taskgroups already added.

One is for FullHD (or widescreen) displays, the other for a vertical (mobile) view.

"""

Taskgrids = [
    {
        "shared": False,
        "locked": False,
        "cards": [
            {
                "size": {
                    "width": 3,
                    "height": 6
                },
                "position": {
                    "y": 0,
                    "x": 0
                },
                "taskgroup": "52fc2c8d-bf7a-4835-bbfe-82d3ddf3742f"
            },
            {
                "size": {
                    "width": 3,
                    "height": 4
                },
                "position": {
                    "y": 11,
                    "x": 0
                },
                "taskgroup": "f7525ffb-0f30-4654-bb72-602fb17247af"
            },
            {
                "size": {
                    "width": 3,
                    "height": 6
                },
                "position": {
                    "y": 6,
                    "x": 0
                },
                "taskgroup": "9d7f146e-1307-47d5-a2cf-bc26f0f515d5"
            },
            {
                "size": {
                    "width": 3,
                    "height": 2
                },
                "position": {
                    "y": 3,
                    "x": 2
                },
                "taskgroup": "48753bc6-4ae0-48ee-ae64-ce41051d9c0d"
            },
            {
                "size": {
                    "width": 3,
                    "height": 2
                },
                "position": {
                    "y": 3,
                    "x": 0
                },
                "taskgroup": "afaa8f83-9584-47b2-91fe-db69f3e7292a"
            },
            {
                "size": {
                    "width": 3,
                    "height": 2
                },
                "position": {
                    "y": 3,
                    "x": 4
                },
                "taskgroup": "10ae31d1-6db8-405b-ac31-a6dcfbce8e8a"
            },
            {
                "size": {
                    "width": 3,
                    "height": 2
                },
                "position": {
                    "y": 11,
                    "x": 4
                },
                "taskgroup": "dee35fe5-5551-479e-843a-359eef15900a"
            },
            {
                "size": {
                    "width": 2,
                    "height": 6
                },
                "position": {
                    "y": 14,
                    "x": 0
                },
                "taskgroup": "f495a4f2-85eb-4b11-a187-a65ce70e9dba"
            },
            {
                "size": {
                    "width": 2,
                    "height": 6
                },
                "position": {
                    "y": 16,
                    "x": 0
                },
                "taskgroup": "3761cbe9-a221-4e25-acaa-4f467596b05a"
            }
        ],
        "name": "FullHD Two Rows",
        "uuid": "c8f61042-6406-4dbf-839f-ab130ca1eb99"
    },
    {
        "shared": False,
        "name": "Mobile",
        "locked": False,
        "cards": [
            {
                "size": {
                    "width": 3,
                    "height": 3
                },
                "position": {
                    "y": 0,
                    "x": 0
                },
                "taskgroup": "52fc2c8d-bf7a-4835-bbfe-82d3ddf3742f"
            },
            {
                "size": {
                    "width": 3
                },
                "position": {
                    "y": 0,
                    "x": 3
                },
                "taskgroup": "afaa8f83-9584-47b2-91fe-db69f3e7292a"
            },
            {
                "size": {
                    "width": 3
                },
                "position": {
                    "y": 0,
                    "x": 4
                },
                "taskgroup": "48753bc6-4ae0-48ee-ae64-ce41051d9c0d"
            },
            {
                "size": {
                    "width": 3,
                    "height": 2
                },
                "position": {
                    "y": 0,
                    "x": 5
                },
                "taskgroup": "10ae31d1-6db8-405b-ac31-a6dcfbce8e8a"
            },
            {
                "size": {
                    "width": 3,
                    "height": 2
                },
                "position": {
                    "y": 0,
                    "x": 7
                },
                "taskgroup": "9d7f146e-1307-47d5-a2cf-bc26f0f515d5"
            },
            {
                "size": {
                    "width": 3,
                    "height": 3
                },
                "position": {
                    "y": 0,
                    "x": 9
                },
                "taskgroup": "f7525ffb-0f30-4654-bb72-602fb17247af"
            },
            {
                "size": {
                    "width": 3,
                    "height": 2
                },
                "position": {
                    "y": 0,
                    "x": 12
                },
                "taskgroup": "3761cbe9-a221-4e25-acaa-4f467596b05a"
            },
            {
                "size": {
                    "width": 3,
                    "height": 2
                },
                "position": {
                    "y": 0,
                    "x": 14
                },
                "taskgroup": "f495a4f2-85eb-4b11-a187-a65ce70e9dba"
            }
        ],
        "description": "<p>Mobile optimized taskgrid</p>",
        "uuid": "ab6c2e36-ff88-4c0c-8830-5d70784af5b8"
    }
]

provision = {'data': Taskgrids, 'model': 'taskgridconfig'}

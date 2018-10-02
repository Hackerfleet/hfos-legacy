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

Provisioning: Taskgroup
=======================

Contains
--------

Some useful/exemplary groups for the default exemplary Taskgrid


"""

Taskgroups = [
    {
        "uuid": "52fc2c8d-bf7a-4835-bbfe-82d3ddf3742f",
        "color": "skyblue",
        "name": "New",
    },
    {
        "uuid": "f7525ffb-0f30-4654-bb72-602fb17247af",
        "color": "lime",
        "name": "Closed",
    },
    {
        "uuid": "9d7f146e-1307-47d5-a2cf-bc26f0f515d5",
        "color": "Orange",
        "name": "In progress",
    },
    {
        "uuid": "48753bc6-4ae0-48ee-ae64-ce41051d9c0d",
        "color": "Yellow",
        "name": "Needs help"
    },
    {
        "uuid": "afaa8f83-9584-47b2-91fe-db69f3e7292a",
        "color": "violet",
        "name": "Postponed",
    },
    {
        "uuid": "10ae31d1-6db8-405b-ac31-a6dcfbce8e8a",
        "color": "salmon",
        "name": "Waiting",
    },
    {
        "uuid": "dee35fe5-5551-479e-843a-359eef15900a",
        "color": "rgb(192, 250, 211)",
        "name": "Expired",
    },
    {
        "uuid": "f495a4f2-85eb-4b11-a187-a65ce70e9dba",
        "color": "rgb(49, 169, 209)",
        "name": "Ideas",
    },
    {
        "uuid": "3761cbe9-a221-4e25-acaa-4f467596b05a",
        "color": "rgb(255, 171, 48)",
        "name": "Contact",
    }
]

provision = {'data': Taskgroups, 'model': 'taskgroup'}

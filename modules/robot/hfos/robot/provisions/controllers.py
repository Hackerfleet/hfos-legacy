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

Controllers = [
    {'name': 'MS0x00 - Logitech Extreme 3D Pro',
     'description': 'Setup for MS0x00 and a Logitech Extreme 3D Pro Joystick',
     'uuid': '5caa7f56-d068-451c-9b69-4efe49d4d5b5',
     'mappings': [
         {
             'controltype': 'analog',
             'controlaxis': 0,
             'controluuid': '51358884-0d61-40a7-acd6-e1f35bbfa3c8'
         },
         {
             'controltype': 'analog',
             'controlaxis': 1,
             'controluuid': '9c4bccbf-17b0-4c8f-bceb-143006287cf7',
         },
         {
             'controltype': 'digital',
             'controlbutton': 0,
             'controluuid': '3136b068-06f5-48e3-9735-cfe77aff0517'
         },
         {
             'controltype': 'digital',
             'controlbutton': 1,
             'controluuid': '18b74670-f069-4ff4-b0e3-7bf812f5fc0e'
         },
         {
             'controltype': 'digital',
             'controlbutton': 2,
             'controluuid': '92968d37-e4a7-4088-b9e8-59787ad0b983'
         },
         {
             'controltype': 'digital',
             'controlbutton': 3,
             'controluuid': 'c85e391d-2586-4157-b386-6b583d5d1934'
         },
     ]}
]


provision = {'data': Controllers, 'model': 'controller'}

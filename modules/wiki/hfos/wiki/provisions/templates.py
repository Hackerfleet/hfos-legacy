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

Provisioning: Wiki - Templates
==============================

Contains
--------

Wiki skeleton for ships


"""

WikiTemplates = [
    {
        'name': 'Protocol',
        'uuid': '14e52e30-4ff7-4d73-9e18-bf9df1803214',
        'title': 'Simple Meeting protocol from $DD$MM$YY',
        'slugtemplate': 'protocol-$DD-$MM-$YY',
        'html': 'This would be a protocol template, once the provision have '
                'been fleshed out.'
    },
    {
        'name': 'Todo',
        'uuid': '88ec45e7-7b12-4450-a8f0-290d51290fa3',
        'title': 'Simple Todo item list for $USER',
        'slugtemplate': 'todo-$USER-$DD-$MM-$YY',
        'html': 'This would be a todo template text, once the provision have '
                'been fleshed out.'
    }
]

provision = {'data': WikiTemplates, 'model': 'wikitemplate'}
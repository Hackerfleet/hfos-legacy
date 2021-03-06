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
Schema: Controllable
====================

Contains
--------

Controllable: Patterns of remote control


"""

from hfos.schemata.defaultform import defaultform
from hfos.schemata.base import base_object

ControllableSchema = base_object('controllable')

ControllableSchema['properties'].update({
    'description': {'type': 'string'},
    'type': {'enum': ['analog', 'digital']},
    'min': {'type': 'integer', 'default': 0},
    'center': {'type': 'integer', 'default': 127},
    'max': {'type': 'integer', 'default': 255},
})

Controllable = {'schema': ControllableSchema, 'form': defaultform}

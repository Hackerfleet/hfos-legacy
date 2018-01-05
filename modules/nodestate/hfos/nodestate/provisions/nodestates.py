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
]


def default_provision(**kwargs):
    provisionList(NodeStates, objectmodels['nodestate'], **kwargs)
    hfoslog('[PROV] Provisioning: Nodestates: Done.')

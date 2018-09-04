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
Hackerfleet Operating System - Backend

Test HFOS Launcher
==================



"""

from hfos.launcher import Core

args = {
    'insecure': False,
    'quiet': False,
    'dev': False,
    'port': 80,
    'host': '127.0.0.1',
    'cert': None,
    'instance': 'testing',
    'blacklist': []
}


def test_launcher():
    """Tests if the Core Launcher can be instantiated"""

    # Use a non privileged port for testing, until that part can be removed
    # from Core

    core = Core(args)

    assert type(core) == Core

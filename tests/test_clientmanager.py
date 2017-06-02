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
Hackerfleet Operating System - Backend

Test HFOS Launcher
==================



"""

from hfos.ui.clientobjects import User, Client
from circuits import Manager
import pytest
from uuid import uuid4
from hfos.ui.clientmanager import ClientManager
from hfos.events.client import authenticationrequest

from pprint import pprint

m = Manager()
cm = ClientManager()
cm.register(m)


def test_instantiate():
    """Tests correct instantiation"""

    assert type(cm) == ClientManager


def transmit(event):
    m.start()

    waiter = pytest.WaitEvent(m, 'send', "hfosweb")

    m.fire(event, "hfosweb")

    result = waiter.wait()
    packet = result.packet

    return packet

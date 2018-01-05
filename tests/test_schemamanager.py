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

from hfos.database import schemastore
from hfos.ui.clientobjects import User, Client
from circuits import Manager
import pytest
from uuid import uuid4
from hfos.ui.schemamanager import SchemaManager
from hfos.events.schemamanager import get, all, configuration
# from hfos.events.client import send

# from pprint import pprint

m = Manager()
sm = SchemaManager()
sm.register(m)

useruuid = uuid4()
clientuuid = uuid4()


def test_instantiate():
    """Tests correct instantiation"""

    assert type(sm) == SchemaManager


def get_schemata(action, data):
    user = User(None, None, useruuid)
    client = Client(None, None, clientuuid, useruuid)

    m.start()

    events = {
        'get': get,
        'all': all,
        'configuration': configuration
    }

    waiter = pytest.WaitEvent(m, 'send', "hfosweb")

    m.fire(events[action](user, action, data, client), "hfosweb")

    result = waiter.wait()
    packet = result.packet

    return packet


def test_schemarequest_all():
    """Tests if the manager reacts with the requested schemastore data"""

    packet = get_schemata('all', None)

    assert packet['action'] == 'all'
    assert packet['component'] == 'hfos.events.schemamanager'
    assert type(packet['data']) == dict


def test_coreschemata():
    """Tests for the supplied basic schemata"""

    base_schemata = [
        'systemconfig', 'client', 'profile', 'user', 'logmessage', 'tag'
    ]

    packet = get_schemata('all', None)
    for schema in base_schemata:
        assert schema in packet['data']


def test_schemarequest_get():
    """Tests if the manager reacts with the requested schemastore data"""

    packet = get_schemata("get", "systemconfig")

    assert packet['action'] == 'get'
    assert packet['component'] == 'hfos.events.schemamanager'
    assert type(packet['data']) == dict
    assert packet['data'] == schemastore['systemconfig']

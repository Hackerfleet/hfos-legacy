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

from hfos.database import objectmodels

from hfos.ui.clientobjects import User, Client
from circuits import Manager
import pytest
from uuid import uuid4
from hfos.ui.configurator import Configurator, get, getlist, put
# from hfos.events.client import send

# from pprint import pprint

m = Manager()
c = Configurator()
c.register(m)

useruuid = str(uuid4())
clientuuid = str(uuid4())


class AccountMock():
    """Mock object for an account"""

    def __init__(self):
        self.name = 'TEST'
        self.roles = ['admin']


class ProfileMock():
    """Mock object for a profile"""

    def __init__(self):
        self.name = 'TEST'


def test_instantiate():
    """Tests correct instantiation"""

    assert type(c) == Configurator


def transmit(action, data, account=AccountMock()):
    """Fire an event and listen for a reply"""

    profile = ProfileMock()
    user = User(account, profile, useruuid)
    client = Client(None, None, clientuuid, useruuid)

    m.start()

    events = {
        'put': put,
        'get': get,
        'getlist': getlist,
    }

    waiter = pytest.WaitEvent(m, "send", "hfosweb")

    m.fire(events[action](user, action, data, client), "hfosweb")

    result = waiter.wait()
    packet = result.packet

    assert packet['component'] == 'hfos.ui.configurator'
    return packet


def test_list():
    """Tests if the configurator returns a valid list of component
    configurations"""

    packet = transmit('getlist', {})

    assert packet['action'] == 'getlist'
    assert len(packet['data']) >= 1


def test_get_object():
    """Tests if a systemconfig can be retrieved"""

    test_component = pytest.TestComponent()
    test_uuid = test_component.config.uuid

    packet = transmit('get', {
        'uuid': test_uuid
    })

    assert packet['action'] == 'get'
    assert 'data' in packet

    obj = packet['data']

    assert obj['uuid'] == test_uuid


def test_get_permission_error():
    """Tests if a systemconfig cannot be retrieved if the user has
    insufficient roles assigned"""

    test_component = pytest.TestComponent()
    test_uuid = test_component.config.uuid

    account = AccountMock()
    account.roles.remove('admin')

    packet = transmit('get', {
        'uuid': test_uuid
    }, account)

    assert packet['action'] == 'get'
    assert 'data' in packet
    assert packet['data'] is False


def test_put():
    test_component = pytest.TestComponent()
    test_uuid = test_component.config.uuid

    packet = transmit('put', {

        'obj': test_component.config.serializablefields(),
        'uuid': test_uuid
    })

    assert packet['data']


def test_put_new_permission_error():
    uuid = str(uuid4())
    obj = objectmodels['systemconfig']({'uuid': uuid})
    obj.active = False
    obj.name = 'TEST SYSTEMCONFIG'

    account = AccountMock()
    account.roles.remove('admin')

    packet = transmit('put', {
        'schema': 'systemconfig',
        'obj': obj.serializablefields(),
        'uuid': uuid
    }, account)

    assert packet['action'] == 'put'
    assert 'data' in packet
    assert packet['data'] is False

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
from random import randint

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""
Hackerfleet Operating System - Backend

Test HFOS Launcher
==================



"""

from circuits import Manager
import pytest
from uuid import uuid4

from hfos.database import objectmodels
from hfos.ui.clientobjects import User, Client
from hfos.ui.objectmanager import ObjectManager
from hfos.events.objectmanager import change, get, delete, put, getlist, search, \
    subscribe, unsubscribe
# objectchange, objectcreation, objectdeletion, objectevent,
# updatesubscriptions,

# from hfos.events.client import send

from pprint import pprint

m = Manager()
om = ObjectManager()
om.register(m)

useruuid = str(uuid4())
clientuuid = str(uuid4())

systemconfig_model = objectmodels['systemconfig']
test_config = systemconfig_model({
    'uuid': str(uuid4()),
    'active': True
})
test_config.save()


class AccountMock():
    def __init__(self):
        self.name = 'TEST'
        self.roles = ['admin']


class ProfileMock():
    def __init__(self):
        self.name = 'TEST'


def test_instantiate():
    """Tests correct instantiation"""

    assert type(om) == ObjectManager


def transmit(action, data, account=AccountMock()):
    """Fire an event and listen for a reply"""

    profile = ProfileMock()
    user = User(account, profile, useruuid)
    client = Client(None, None, clientuuid, useruuid)

    m.start()

    events = {
        'put': put,
        'get': get,
        'delete': delete,
        'change': change,
        'getlist': getlist,
        'search': search,
        'subscribe': subscribe,
        'unsubscribe': unsubscribe
    }

    waiter = pytest.WaitEvent(m, "send", "hfosweb")

    m.fire(events[action](user, action, data, client), "hfosweb")

    result = waiter.wait()
    packet = result.packet

    assert packet['component'] == 'hfos.events.objectmanager'
    return packet


def test_unfiltered_list():
    """Tests if the objectmanager returns a valid list of objects"""

    packet = transmit('getlist', {
        'schema': 'systemconfig'
    })

    assert packet['action'] == 'getlist'
    assert type(packet['data']) == dict
    assert 'schema' in packet['data']
    assert 'list' in packet['data']
    assert len(packet['data']['list']) >= 1


def test_list_all_fields():
    """Tests if a list request with * fields returns at least a subset of
    all the default fields of a systemconfig"""

    packet = transmit('getlist', {
        'schema': 'systemconfig',
        'fields': '*'
    })

    assert packet['action'] == 'getlist'

    obj = packet['data']['list'][0]

    assert 'uuid' in obj
    assert 'active' in obj


def test_no_schema():
    """Tests if unspecified schema leads to 'noschema' error feedback"""

    packet = transmit('get', {
    })

    assert packet['action'] == 'fail'


def test_invalid_schema():
    """Tests if an error is returned when a not existing schema is requested"""

    packet = transmit('getlist', {
        'schema': 'BERTRAM'
    })

    assert packet['action'] == 'fail'


def test_search():
    """Tests if simple searching of objects works"""

    packet = transmit('search', {
        'schema': 'systemconfig',
        'search': "{'active': True}",
        'req': 5
    })

    assert packet['action'] == 'search'

    data = packet['data']

    assert data['req'] == 5
    assert data['schema'] == 'systemconfig'

    assert len(data['list']) >= 1


def test_get_object_invalid():
    """Tests if an error is returned when a not existing object is requested"""

    packet = transmit('get', {
        'schema': 'systemconfig',
        'uuid': 'BERTRAM'
    })

    assert packet['action'] == 'fail'
    assert 'unavailable' in packet['data']['reason']


def test_get_schema_invalid():
    """Tests if an error is returned when a not existing object is requested"""

    packet = transmit('get', {
        'uuid': 'BERTRAM'
    })

    assert packet['action'] == 'fail'
    assert packet['data']['reason'] is 'no_schema'


def test_get_object():
    """Tests if a systemconfig can be retrieved"""

    system_configs = transmit('getlist', {
        'schema': 'systemconfig'
    })['data']['list']
    system_config_uuid = system_configs[0]['uuid']

    packet = transmit('get', {
        'schema': 'systemconfig',
        'uuid': system_config_uuid
    })

    assert packet['action'] == 'get'
    assert 'data' in packet

    obj = packet['data']

    assert obj['uuid'] == system_config_uuid


def test_get_permission_error():
    """Tests if a systemconfig cannot be retrieved if the user has
    insufficient roles assigned"""

    system_configs = transmit('getlist', {
        'schema': 'systemconfig'
    })['data']['list']
    system_config_uuid = system_configs[0]['uuid']

    account = AccountMock()
    account.roles.remove('admin')

    request_id = randint(23, 42)

    packet = transmit('get', {
        'schema': 'systemconfig',
        'uuid': system_config_uuid,
        'req': request_id
    }, account)

    assert packet['action'] == 'fail'
    assert 'data' in packet

    data = packet['data']

    assert data['reason'] == 'No permission'

    assert data['req'] == request_id


def test_list_filtered():
    """Tests if a systemconfig can be retrieved by filter"""

    packet = transmit('getlist', {
        'schema': 'systemconfig',
        'filter': {'active': True},
        'fields': ['active']
    })

    assert packet['action'] == 'getlist'
    assert 'data' in packet
    assert packet['data']['schema'] == 'systemconfig'

    result = packet['data']['list']

    assert len(result) > 0
    for item in result:
        assert item['active']


def test_subscribe():
    """Tests if subscribing to an object works"""

    system_configs = transmit('getlist', {
        'schema': 'systemconfig'
    })['data']['list']
    system_config_uuid = system_configs[0]['uuid']

    packet = transmit('subscribe', system_config_uuid)
    pprint(packet)
    assert packet['data']['success']
    assert packet['data']['uuid'] == [system_config_uuid]


def test_unsubscribe():
    """Tests if unsubscribing to an object works"""

    system_configs = transmit('getlist', {
        'schema': 'systemconfig'
    })['data']['list']
    system_config_uuid = system_configs[0]['uuid']

    packet = transmit('unsubscribe', system_config_uuid)
    pprint(packet)
    assert packet['data']['success']
    assert packet['data']['uuid'] == [system_config_uuid]


def test_put_new():
    uuid = str(uuid4())
    obj = objectmodels['systemconfig']({'uuid': uuid})
    obj.active = False
    obj.name = 'TEST SYSTEMCONFIG'

    packet = transmit('put', {
        'schema': 'systemconfig',
        'obj': obj.serializablefields(),
        'uuid': uuid
    })
    pprint(packet)
    assert packet['data']['object']
    assert packet['data']['schema'] == 'systemconfig'
    assert packet['data']['uuid'] == uuid


def test_put_new_permission_error():
    uuid = str(uuid4())
    obj = objectmodels['systemconfig']({'uuid': uuid})
    obj.active = False
    obj.name = 'TEST SYSTEMCONFIG'
    request_id = randint(23, 42)

    account = AccountMock()
    account.roles.remove('admin')

    packet = transmit('put', {
        'schema': 'systemconfig',
        'obj': obj.serializablefields(),
        'uuid': uuid,
        'req': request_id
    }, account)

    assert packet['action'] == 'fail'
    assert 'data' in packet

    data = packet['data']

    assert data['reason'] == 'No permission'
    assert data['req'] == request_id


def test_delete():
    uuid = str(uuid4())

    obj = objectmodels['systemconfig']({'uuid': uuid})
    obj.active = False
    obj.name = 'TEST SYSTEMCONFIG'

    packet = transmit('put', {
        'schema': 'systemconfig',
        'obj': obj.serializablefields(),
        'uuid': uuid
    })

    assert packet['action'] == 'put'
    assert packet['data']['uuid'] == uuid

    packet = transmit('delete', {
        'schema': 'systemconfig',
        'uuid': uuid
    })

    assert packet['data']['schema'] == 'systemconfig'
    assert packet['data']['uuid'] == uuid


def test_delete_invalid_object():
    packet = transmit('delete', {
        'schema': 'systemconfig',
        'uuid': 'FOOBAR'
    })
    pprint(packet)
    assert packet['action'] == 'fail'
    assert packet['data']['reason'] == 'not found'

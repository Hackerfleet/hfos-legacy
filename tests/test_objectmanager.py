"""
Hackerfleet Operating System - Backend

Test HFOS Launcher
==================


:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.database import initialize

initialize()  # Set up database access for testing once

from hfos.database import schemastore, objectmodels

from hfos.ui.clientobjects import User, Client
from circuits import Manager
import pytest
from uuid import uuid4
from hfos.ui.objectmanager import ObjectManager
from hfos.events.system import objectmanagerrequest

from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

m = Manager()
sm = ObjectManager().register(m)

useruuid = uuid4()
clientuuid = uuid4()


def test_instantiate():
    """Tests correct instantiation"""

    assert type(sm) == ObjectManager


def transmit(action, data):
    user = User(None, None, useruuid)
    client = Client(None, None, clientuuid, useruuid)

    m.start()

    waiter = pytest.WaitEvent(m, 'send', "hfosweb")

    m.fire(objectmanagerrequest(user, action, data, client), "hfosweb")

    result = waiter.wait()
    packet = result.packet

    assert packet['component'] == 'objectmanager'
    return packet


system_configs = transmit('list', {
    'schema': 'systemconfig'
})['data']['list']
system_config_uuid = system_configs[0]['uuid']
pprint(system_config_uuid)


def test_unfiltered_list():
    """Tests if the objectmanager returns a valid list of objects"""

    packet = transmit('list', {
        'schema': 'systemconfig'
    })

    assert packet['action'] == 'list'
    assert type(packet['data']) == dict
    assert 'schema' in packet['data']
    assert 'list' in packet['data']
    assert len(packet['data']['list']) >= 1


def test_list_all_fields():
    """Tests if a list request with * fields returns at least a subset of
    all the default fields of a systemconfig"""

    packet = transmit('list', {
        'schema': 'systemconfig',
        'fields': '*'
    })

    assert packet['action'] == 'list'

    obj = packet['data']['list'][0]

    assert 'uuid' in obj
    assert 'active' in obj


def test_no_schema():
    """Tests if unspecified schema leads to 'noschema' error feedback"""

    packet = transmit('get', {
    })

    assert packet['action'] == 'noschema'


def test_invalid_schema():
    """Tests if an error is returned when a not existing schema is requested"""

    packet = transmit('list', {
        'schema': 'BERTRAM'
    })

    assert packet['action'] == 'noschema'


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

    assert packet['action'] == 'noobject'


def test_get_object():
    """Tests if a systemconfig can be retrieved"""

    packet = transmit('get', {
        'schema': 'systemconfig',
        'uuid': system_config_uuid
    })

    assert packet['action'] == 'get'
    assert 'data' in packet

    obj = packet['data']

    assert obj['uuid'] == system_config_uuid


def test_list_filtered():
    """Tests if a systemconfig can be retrieved by filter"""

    packet = transmit('list', {
        'schema': 'systemconfig',
        'filter': {'active': True},
        'fields': ['active']
    })

    assert packet['action'] == 'list'
    assert 'data' in packet
    assert packet['data']['schema'] == 'systemconfig'

    result = packet['data']['list']

    assert len(result) > 0
    for item in result:
        assert item['active']


def test_subscribe():
    """Tests if subscribing to an object works"""

    packet = transmit('subscribe', system_config_uuid)

    assert packet['data']['success']
    assert packet['data']['uuid'] == system_config_uuid


def test_unsubscribe():
    """Tests if unsubscribing to an object works"""

    packet = transmit('unsubscribe', system_config_uuid)

    assert packet['data']['success']
    assert packet['data']['uuid'] == system_config_uuid


def test_put_new():
    obj = objectmodels['systemconfig']()
    obj.active = False
    obj.uuid = str(uuid4())
    obj.name = 'TEST SYSTEMCONFIG'

    packet = transmit('put', {
        'schema': 'systemconfig',
        'obj': obj.serializablefields(),
        'uuid': 'create'
    })

    assert packet['data'][0]

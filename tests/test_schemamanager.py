"""
Hackerfleet Operating System - Backend

Test HFOS Launcher
==================


:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.database import initialize, schemastore
from hfos.ui.clientobjects import User, Client
from circuits import Manager
import pytest
from uuid import uuid4
from hfos.ui.schemamanager import SchemaManager
from hfos.events.system import schemarequest

from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

initialize()  # Set up database access for testing once

m = Manager()
sm = SchemaManager().register(m)

useruuid = uuid4()
clientuuid = uuid4()


def test_instantiate():
    """Tests correct instantiation"""

    assert type(sm) == SchemaManager


def get_schemata(request=None):
    request_type = "All" if not request else "Get"

    user = User(None, None, useruuid)
    client = Client(None, None, clientuuid, useruuid)

    m.start()

    waiter = pytest.WaitEvent(m, 'send', "hfosweb")

    m.fire(schemarequest(user, request_type, request, client), "hfosweb")

    result = waiter.wait()
    packet = result.packet

    return packet


def test_schemarequest_all():
    """Tests if the manager reacts with the requested schemastore data"""

    packet = get_schemata()

    assert packet['action'] == 'All'
    assert packet['component'] == 'schema'
    assert type(packet['data']) == dict


def test_coreschemata():
    """Tests for the supplied basic schemata"""

    base_schemata = [
        'systemconfig', 'client', 'profile', 'user', 'logmessage', 'tag'
    ]

    packet = get_schemata()
    for schema in base_schemata:
        assert schema in packet['data']


def test_schemarequest_get():
    """Tests if the manager reacts with the requested schemastore data"""

    packet = get_schemata(request="systemconfig")

    assert packet['action'] == 'Get'
    assert packet['component'] == 'schema'
    assert type(packet['data']) == dict
    assert packet['data'] == schemastore['systemconfig']

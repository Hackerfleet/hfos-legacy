"""
Hackerfleet Operating System - Backend

Test HFOS Launcher
==================


:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.ui.clientobjects import User, Client
from circuits import Manager
import pytest
from uuid import uuid4
from hfos.ui.clientmanager import ClientManager
from hfos.events.client import authenticationrequest

from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

m = Manager()
cm = ClientManager().register(m)


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

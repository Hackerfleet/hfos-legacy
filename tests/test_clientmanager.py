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

from circuits import Manager
# from circuits.web.websockets.client import WebSocketClient
# from circuits.web.websockets.dispatcher import WebSocketsDispatcher
# from circuits.web.servers import TCPServer
from circuits.net.events import read  # , write
from json import dumps  # , loads
import pytest
from uuid import uuid4
from hfos.ui.clientmanager import ClientManager
# from hfos.events.client import authenticationrequest

from pprint import pprint

m = Manager()

cm = ClientManager()
cm.register(m)


def test_instantiate():
    """Tests correct instantiation"""

    assert type(cm) == ClientManager


def transmit(event_in, channel_in, event_out, channel_out):
    """Fire an event and listen for a reply"""

    waiter = pytest.WaitEvent(m, event_in, channel_in)

    m.fire(event_out, channel_out)

    result = waiter.wait()

    return result


def test_auth_request():
    """Test if clientmanager fires an authentication-request on login"""

    m.start()

    data = {
        'component': 'auth',
        'action': 'login',
        'data': {
            'username': 'foo',
            'password': 'bar'
        }
    }

    event = read(None, dumps(data))

    result = transmit('authenticationrequest', 'auth', event, 'wsserver')

    assert result.username == 'foo'
    assert result.password == 'bar'


def test_auto_auth_request():
    m.start()

    client_config_uuid = str(uuid4())

    data = {
        'component': 'auth',
        'action': 'autologin',
        'data': {
            'uuid': client_config_uuid

        }
    }

    event = read(None, dumps(data))

    result = transmit('authenticationrequest', 'auth', event, 'wsserver')

    pprint(result.__dict__)
    assert result.auto is True
    assert result.requestedclientuuid['uuid'] == client_config_uuid


def test_auth_logout():
    return
    m.start()

    client_uuid = str(uuid4())

    data = {
        'component': 'auth',
        'action': 'logout',
        'data': {}
    }

    event = read(None, dumps(data))

    result = transmit('clientdisconnect', 'hfosweb', event, 'wsserver')

    assert result.clientuuid == client_uuid


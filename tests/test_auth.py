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

Test HFOS Auth
==============



"""

from circuits import Manager
import pytest
from hfos.ui.auth import Authenticator
from hfos.events.client import authenticationrequest, authentication
from hfos.tools import std_uuid
import hfos.logger as logger

# from pprint import pprint

m = Manager()

auth = Authenticator()
auth.register(m)


def test_instantiate():
    """Tests correct instantiation"""

    assert type(auth) == Authenticator


def transmit(event_in, channel_in, event_out, channel_out):
    """Fire an event and listen for a reply"""

    waiter = pytest.WaitEvent(m, event_in, channel_in)

    m.fire(event_out, channel_out)

    result = waiter.wait()

    return result


def test_invalid_user_auth():
    """Test if login with invalid credentials fails"""

    log = logger.LiveLog
    logger.live = True

    m.start()

    client_uuid = std_uuid()
    event = authenticationrequest(
        username='test',
        password='test',
        clientuuid=client_uuid,
        requestedclientuuid=client_uuid,
        sock=None,
        auto=False
    )

    result = transmit('authentication', 'auth', event, 'auth')

    assert result is None
    assert "No userobject due to error" in str(log)


def test_createuser():
    """Test if auth correctly creates a new user"""

    class createuser_event():
        """Mock event to request creation of new user"""

        def __init__(self):
            self.username = 'test_user'
            self.password = 'test_password'
            self.clientuuid = std_uuid()
            self.sock = None

    m.start()

    waiter = pytest.WaitEvent(m, 'authentication', 'auth')

    auth.createuser(createuser_event())

    result = waiter.wait()

    assert type(result) == authentication

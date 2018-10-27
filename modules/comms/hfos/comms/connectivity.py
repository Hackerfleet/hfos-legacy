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

Module: Connectivity Monitor
============================

The Connectivity Monitor regularly checks if it can reach a configured 
host to see if the node is currently online.

"""

import socket
from time import time
from hfos.component import ConfigurableComponent, handler
from hfos.database import objectmodels
from hfos.logger import error, warn, hilight, debug, verbose
from hfos.nodestate.manager import backend_nodestate_toggle
from circuits import Timer, Event

from hfos.debugger import cli_register_event

STATE_UUID_CONNECTIVITY = '6d650454-e9b1-40ca-94a6-be817deb5448'


# CLI events

class cli_test_connectivity(Event):
    """Triggers a connectivity check"""
    pass


class timed_connectivity_check(Event):
    """Regular timed connectivity check"""
    pass


# Components


class ConnectivityMonitor(ConfigurableComponent):
    """
    Monitors connectivity changes and online capabilities.
    """

    configprops = {
        'host': {'type': 'string', 'default': ''},
        'port': {'type': 'integer', 'default': 80},
        'timeout': {'type': 'integer', 'default': 30},
        'interval': {'type': 'integer', 'default': 30}
    }
    channel = "hfosweb"

    def __init__(self, *args):
        super(ConnectivityMonitor, self).__init__("NETMON", *args)

        self.fireEvent(cli_register_event('test_connectivity', cli_test_connectivity))

        self.old_status = True
        self.status = False

        self.nodestate = objectmodels['nodestate'].find_one({'uuid': STATE_UUID_CONNECTIVITY})

        status = self._can_connect()
        self.log('Initial connectivity state:', status)
        self.fireEvent(backend_nodestate_toggle(STATE_UUID_CONNECTIVITY, on=status, force=True))
        self.old_status = self.status = status

        self.timer = Timer(self.config.interval, timed_connectivity_check(), persist=True).register(self)

        self.log("Started")

    @handler("cli_test_connectivity")
    def cli_test_connectivity(self, *args):
        """CLI command to ad-hoc test connectivity"""
        self.log('Checking network uplink')

        if self._can_connect():
            msg = 'This node has internet connectivity to %s:%i'
        else:
            msg = 'This node seems offline and cannot reach %s:%i'

        self.log(msg % (self.config.host, self.config.port))

    def timed_connectivity_check(self, event):
        """Tests internet connectivity in regular intervals and updates the nodestate accordingly"""
        self.status = self._can_connect()
        self.log('Timed connectivity check:', self.status, lvl=verbose)

        if self.status:
            if not self.old_status:
                self.log('Connectivity gained')
                self.fireEvent(backend_nodestate_toggle(STATE_UUID_CONNECTIVITY, on=True, force=True))
        else:
            if self.old_status:
                self.log('Connectivity lost', lvl=warn)
                self.old_status = False
                self.fireEvent(backend_nodestate_toggle(STATE_UUID_CONNECTIVITY, off=True, force=True))

        self.old_status = self.status

    def _can_connect(self):
        """Tries to connect to the configured host:port and returns True if the connection was established"""
        self.log('Trying to reach configured connectivity check endpoint', lvl=verbose)

        try:
            socket.setdefaulttimeout(self.config.timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.config.host, self.config.port))
            return True
        except Exception as ex:
            self.log(ex, pretty=True, lvl=debug)
            return False

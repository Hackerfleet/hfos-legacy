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


Module NotificationManager
==========================


"""

from circuits import Event
from hfos.component import ConfigurableComponent, handler
from hfos.debugger import cli_register_event
from hfos.logger import events, verbose, debug, warn, critical, error, hilight

from . import notify


class cli_test_notify(Event):
    """Initiates a notification subsystem test"""
    pass


class NotificationManager(ConfigurableComponent):
    """Handles user notifications and their escalation"""

    configprops = {}

    def __init__(self, *args, **kwargs):
        super(NotificationManager, self).__init__('NOTIFY', *args, **kwargs)

        self.log("Started")
        self.fireEvent(cli_register_event('test_notify', cli_test_notify))

    @handler("cli_test_notify")
    def cli_test_notify(self, event):
        """Run a notification subsystem test"""

        self.log('Notifying test running:')
        self.fireEvent(notify('FOO', 'NotificationTest', 'This is only a test!', 9, {}))

    def notify(self, event):
        """Notify a user"""

        self.log('Got a notification event!')

        self.log(event, pretty=True)
        self.log(event.__dict__)

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

Module: Session Manager
=======================

The Session Manager checks and administrates sessions.

"""

import os
from time import time
from hfos.component import ConfigurableComponent, handler, authorizedevent
from hfos.database import objectmodels
from hfos.logger import error, warn, hilight, debug, verbose
from circuits import Timer, Event

from hfos.debugger import cli_register_event


# CLI events

class cli_test_Session(Event):
    """Triggers a Session check"""
    pass


class session_attach_file(authorizedevent):
    pass


# Components


class SessionManager(ConfigurableComponent):
    """
    Manages Session edits
    """

    configprops = {}
    channel = "hfosweb"

    def __init__(self, *args):
        super(SessionManager, self).__init__("SESSION", *args)

        self.fireEvent(cli_register_event('test_Session', cli_test_Session))

        self.log("Started")



    @handler("cli_test_Session")
    def cli_test_Session(self, *args):
        """CLI command to ad-hoc test Session"""
        self.log('Checking sessions')

    @handler(session_attach_file)
    def session_attach_file(self, event):
        self.log('Received attachment for session')

        name = event.data['name']
        self.log(name)

        # self.log(event.data['raw'])

        path = os.path.join(self.storagepath, event.user.uuid)
        filename = os.path.join(path, name)
        os.makedirs(path)

        with open(filename, 'wb') as f:
            f.write(event.data['raw'])

        notification = {
            'component': 'hfos.session.manager',
            'action': 'session_attach_file',
            'data': {
                'msg': 'Attachement stored',
                'type': 'success'
            }
        }
        self.fireEvent(send(event.client.uuid, notification))

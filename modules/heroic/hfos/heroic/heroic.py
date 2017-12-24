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


Module: Heroic
==============

Listens to events and adds achievements accordingly


"""

from hfos.component import ConfigurableComponent, handler
from hfos.database import objectmodels
from hfos.logger import hfoslog, error, warn, critical, events
from hfos.events.system import authorizedevent
from pprint import pprint


class Heroic(ConfigurableComponent):
    """
    Watches for authorized events and adds achievements to a user's profile.
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the Heroic component.

        :param args:
        """

        super(Heroic, self).__init__("HEROIC", *args)

        self.log("Started")
        self.accounts = {}

        for account in objectmodels['user'].find():
            self.accounts[account.uuid] = account

        self.log('Cached', len(self.accounts), 'User accounts')

    #@handler()
    #def authorized_event_handler(self, event, *args, **kwargs):
    #    self.log(event, args, kwargs)
        #if isinstance(event, authorizedevent):
        #    self.log('Event:', event)
        #    account = self.accounts[event.useruuid]
        #    self.log('Account', account)
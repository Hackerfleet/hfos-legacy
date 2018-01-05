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

Module: ActivityMonitor
=======================

Surveillance piece to check out what the users are doing, so the system can
react
accordingly (e.g. not disturb with unimportant alerts when user is actively
doing something)

Possibilities:
* check if users noticed an alert
* notify users, about what other users are doing
* offer further information
* achievements ;) (stared 100 hours at the map)

Should be user configurable and toggleable, at least most parts/bits.


"""

from hfos.component import handler
from hfos.events.client import send
from hfos.component import ConfigurableComponent
from hfos.logger import error, verbose  # , warn, critical


class ActivityMonitor(ConfigurableComponent):
    """
    ActivityMonitor manager

    Handles
    * incoming ActivityMonitor messages
    * ActivityMonitor broadcasts
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(ActivityMonitor, self).__init__('ACTIVITY', *args)

        self.log("Started")

        self.referenceframe = None
        self.alertlist = []

    @handler('referenceframe', channel='navdata')
    def referenceframe(self, event):
        """Handles navigational reference frame updates.
        These are necessary to assign geo coordinates to alerts and other
        misc things.

        :param event with incoming referenceframe message
        """

        self.log("Got a reference frame update! ", event, lvl=verbose)

        self.referenceframe = event.data

    def userlogin(self, event):
        """Checks if an alert is ongoing and alerts the newly connected
        client, if so."""

        clientuuid = event.clientuuid

    def activityrequest(self, event):
        """ActivityMonitor event handler for incoming events

        :param event with incoming ActivityMonitor message
        """

        # self.log("Event: '%s'" % event.__dict__)

        try:
            action = event.action
            data = event.data
            self.log("Activityrequest: ", action, data)

        except Exception as e:
            self.log("Error: '%s' %s" % (e, type(e)), lvl=error)

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

Module: AlertManager
====================

AlertManager


"""

from hfos.component import ConfigurableComponent, handler, authorizedevent
from hfos.logger import error, warn, verbose, critical, events
from hfos.events.client import broadcast, send


class alert(authorizedevent):
    """Toggles an Alert"""


class Manager(ConfigurableComponent):
    """
    Alert manager

    Handles
    * incoming alert messages
    * alert broadcasts
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(Manager, self).__init__("ALERT", *args)

        self.log("Started")

        self.reference_frame = None
        self.mob_alert = False
        self.alerts = []

    @handler('referenceframe', channel='navdata')
    def referenceframe(self, event):
        """Handles navigational reference frame updates.
        These are necessary to assign geo coordinates to alerts and other
        misc things.

        :param event with incoming referenceframe message
        """

        self.log("Got a reference frame update! ", event, lvl=events)

        self.reference_frame = event.data

    def userlogin(self, event):
        """Checks if an alert is ongoing and alerts the newly connected
        client, if so."""

        client_uuid = event.clientuuid

        if self.mob_alert:
            alert_packet = {
                'component': 'hfos.alert.manager',
                'action': 'alert',
                'data': True
            }
            self.fireEvent(send(client_uuid, alert_packet))

    def _record_mob_alert(self):
        self.alerts.append(self.reference_frame)

    @handler(alert)
    def alert(self, event):
        """AlertManager event handler for incoming events

        :param event with incoming AlertManager message
        """

        self.log("Event: '%s'" % event.__dict__)
        try:
            data = event.data

            # noinspection PySimplifyBooleanCheck,PySimplifyBooleanCheck
            if data is True:
                self.log("MOB ALERT ACTIVATED.", lvl=critical)

                self.mob_alert = True
                self._record_mob_alert()

                alert_packet = {
                    'component': 'hfos.alert.manager',
                    'action': 'alert',
                    'data': True
                }
            else:
                self.log("MOB deactivation requested by ",
                         event.user.account.name, lvl=warn)
                self.mob_alert = False

                alert_packet = {
                    'component': 'hfos.alert.manager',
                    'action': 'alert',
                    'data': False
                }

            try:
                self.fireEvent(broadcast("users", alert_packet))
            except Exception as e:
                self.log("Transmission error before broadcast: %s" % e,
                         lvl=error)

        except Exception as e:
            self.log("Error: '%s' %s" % (e, type(e)), lvl=error)

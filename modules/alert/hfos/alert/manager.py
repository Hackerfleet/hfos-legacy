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

from circuits import Event

from hfos.component import ConfigurableComponent, handler, authorizedevent
from hfos.logger import error, warn, verbose, critical, events
from hfos.debugger import cli_register_event
from hfos.events.client import broadcast, send


# TODO: The client/backend communication overlaps with the notification system and should be separated

class trigger(authorizedevent):
    """Triggers an Alert"""


class cancel(authorizedevent):
    """Cancels an Alert"""


class backend_trigger(Event):
    """Triggers an alert from backend components"""

    def __init__(self, alert, *args):
        super(backend_trigger, self).__init__(*args)
        self.alert = alert


class backend_cancel(Event):
    """Triggers an alert from backend components"""

    def __init__(self, topic, *args):
        super(backend_cancel, self).__init__(*args)
        self.topic = topic


class backend_notify(Event):
    """Triggers an alert from backend components"""

    def __init__(self, category, title, message, role='all', duration=20, *args):
        super(backend_notify, self).__init__(*args)
        self.category = category
        self.title = title
        self.message = message
        self.role = role
        self.duration = duration

class cli_show_alerts(Event):
    pass

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

        self.reference_frame = None
        self.clients = {}
        self.alerts = {}

        self.fireEvent(cli_register_event('alert_show', cli_show_alerts))

        self.log("Started")

    @handler('cli_show_alerts')
    def show_alerts(self, event):
        self.log(self.alerts, pretty=True)

    @handler('referenceframe', channel='navdata')
    def referenceframe(self, event):
        """Handles navigational reference frame updates.
        These are necessary to assign geo coordinates to alerts and other
        misc things.

        :param event with incoming referenceframe message
        """

        self.log("Got a reference frame update! ", event, lvl=events)

        self.reference_frame = event.data

    @handler('backend_trigger')
    def backend_trigger(self, event):
        self._trigger(event, event.alert)

    @handler('backend_cancel')
    def backend_cancel(self, event):
        self._cancel(event.topic)

    @handler('backend_notify')
    def backend_notify(self, event):
        role = event.role
        for client_uuid, user in self.clients.items():
            if role != 'all':
                if role not in user.roles:
                    continue

            alert_packet = {
                'component': 'hfos.alert.manager',
                'action': 'notify',
                'data': {
                    'type': event.category,
                    'title': event.title,
                    'message': event.message,
                    'duration': event.duration
                }
            }

            self.fireEvent(send(client_uuid, alert_packet))

    def userlogin(self, event):
        """Checks if an alert is ongoing and alerts the newly connected
        client, if so."""

        client_uuid = event.clientuuid

        self.log(event.user, pretty=True)

        self.log('Adding client')
        self.clients[event.clientuuid] = event.user

        for topic, alert in self.alerts.items():
            self.alert(client_uuid, alert)

    def userlogout(self, event):
        if event.clientuuid in self.clients:
            self.log('Removing client')
            self.clients.pop(event.clientuuid)

    def alert(self, client_uuid, alert):
        if alert['role'] != 'all':
            user = self.clients[client_uuid]
            if alert['role'] not in user.roles:
                return

        alert_packet = {
            'component': 'hfos.alert.manager',
            'action': 'trigger',
            'data': {
                'title': alert['topic'] + ' alert',
                'message': alert['message']
            }
        }

        self.fireEvent(send(client_uuid, alert_packet))

    def _broadcast(self, alert):
        self.log('Broadcasting new alert to all users:', alert)

        for client in self.clients:
            self.alert(client, alert)

    def _record_alert(self, event, alert):
        alert['reference_frame'] = self.referenceframe
        if isinstance(event, authorizedevent):
            alert['originator'] = event.user.uuid
        else:
            alert['originator'] = 'SYSTEM'

        self.log('Before:', self.alerts, pretty=True)
        self.alerts[alert['topic']] = alert
        self.log('Alerts:', self.alerts, pretty=True)

    @handler(trigger)
    def trigger(self, event):
        """AlertManager event handler for incoming events

        :param event with incoming AlertManager message
        """

        topic = event.data.get('topic', None)
        if topic is None:
            self.log('No alert topic to trigger', lvl=warn)
            return

        alert = {
            'topic': topic,
            'message': event.data.get('msg', 'Alert has been triggered'),
            'role': event.data.get('role', 'all')
        }

        self._trigger(event, alert)

    def _trigger(self, event, alert):
        self.log('Triggering alert topic', lvl=verbose)
        if alert['topic'] in self.alerts:
            self.log('Alert already triggered')
            return

        self._record_alert(event, alert)

        self._broadcast(alert)

    @handler(cancel)
    def cancel(self, event):
        """AlertManager event handler for incoming events

        :param event with incoming AlertManager message
        """

        topic = event.data.get('topic', None)
        if topic is None:
            self.log('No alert topic to cancel', lvl=warn)
            return
        self._cancel(topic)

    def _cancel(self, topic):
        self.log('Cancelling alert topic', lvl=verbose)
        if topic in self.alerts:
            cancel_packet = {
                'component': 'hfos.alert.manager',
                'action': 'cancel',
                'data': topic
            }
            role = self.alerts[topic]['role']

            for client_uuid, user in self.clients.items():
                try:
                    if role != 'all':
                        if role not in user.roles:
                            continue

                    self.fireEvent(send(client_uuid, cancel_packet))
                except Exception as e:
                    self.log("Transmission error before broadcast: %s" % e,
                             lvl=error)

            self.alerts.pop(topic)
        else:
            self.log('Tried to cancel non existing alert:', topic, lvl=warn)

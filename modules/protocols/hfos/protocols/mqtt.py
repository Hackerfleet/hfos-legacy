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
from random import randint

import struct
from circuits.core.events import Event
from circuits.core.timers import Timer
from hfos.logger import hilight

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""

Module: MQTTGateway
======================

Doing rather not much except serve as module component entrypoint.


"""

from hfos.component import ConfigurableComponent, handler
from paho.mqtt import client as mqtt
from paho.mqtt import publish
from hfos.navdata.events import referenceframe


class MQTTGateway(ConfigurableComponent):
    """
    Bidirectional MQTT-based message queuing gateway.
    """

    configprops = {}

    channel = 'hfosweb'

    def __init__(self, **kwargs):
        super(MQTTGateway, self).__init__('MQTT', **kwargs)
        self.log("Started.")

        self.client = mqtt.Client()
        self.host = 'localhost'
        self.port = 1883
        self.timeout = 60

        self.subscriptions = ['test/#']

        self.topic = 'hfos'

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        #self.timer = Timer(5, Event.create('publish'), persist=True).register(self)

    def ready(self, *args):
        self.log('Connecting to MQTT broker:', self.host)

        #self.client.connect(self.host, self.port, self.timeout)
        #self.client.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        self.log("Connected:", client, userdata, flags, rc)

        for subscription in self.subscriptions:
            self.client.subscribe(subscription)

    def _on_message(self, client, userdata, msg):
        self.log('Message:', msg.topic, msg.payload, client, userdata, pretty=True)
        self.log(msg.__dict__, pretty=True)

    def publish(self):
        self.client.publish("test/value", randint(0, 255))

    @handler("referenceframe", channel='navdata')
    def referenceframe(self, event):
        # self.log('MQTT received sensordata')

        messages = []

        for entry in event.data['data']:
            data = event.data['data'][entry]
            # self.log('Entry:', entry, 'Data:', data, type(data), pretty=True, lvl=hilight)
            msg = {
                'topic': self.topic + "/" + entry,
                'payload': str(data)
            }
            messages.append(msg)

        if len(messages) > 0:
            publish.multiple(messages)

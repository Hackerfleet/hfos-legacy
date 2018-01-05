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


Module NMEA
===========


"""

from circuits import Timer, Event
from hfos.component import ConfigurableComponent
from hfos.logger import verbose, debug, warn, critical, error
from hfos.navdata.bus import serial_packet


class SensorPlayback(ConfigurableComponent):
    """
    Plays back previously recorded NMEA/AIS/etc log files. Handy for
    debugging and demoing purposes.
    """

    configprops = {
        'delay': {
            'type': 'integer',
            'title': 'Delay',
            'description': 'Delay between messages (milliseconds)',
            'default': 5000
        },
        'logfile': {
            'type': 'string',
            'title': 'Filename',
            'description': 'Name of log file to replay',
            'default': ''
        },
    }
    configform = [
        'delay',
        'logfile'
    ]

    channel = "serial"

    def __init__(self, *args, **kwargs):
        super(SensorPlayback, self).__init__('SENSORPLAYBACK', *args, **kwargs)
        self.log("Playback component started with", self.config.delay,
                 "milliseconds interval.")

        if self.config.logfile != '' and self.config.active:
            with open(self.config.logfile, 'r') as logfile:
                self.logdata = logfile.readlines()
            self.length = len(self.logdata)

            self.log("Logfile contains", self.length, "items.")

            self.position = 0

            self.timer = Timer(self.config.delay / 1000.0, Event.create(
                'sensor_playback'), persist=True).register(self)
        else:
            self.log("No logfile specified and/or deactivated.", lvl=warn)

    def sensor_playback(self, *args):
        self.log("Playback time", lvl=verbose)
        try:
            if self.position == len(self.logdata):
                self.log("Playback looping", lvl=warn)
                self.position = 0
            else:
                self.position += 1

            data = self.logdata[self.position]

            self.log("Transmitting: ", data, lvl=verbose)

            self.fireEvent(serial_packet('SIMULATION', data))

            if self.position % 100 == 0:
                self.log("Played back", self.position, "sentences.")

        except Exception as e:
            self.log("Error during logdata playback: ", e, type(e), lvl=error)

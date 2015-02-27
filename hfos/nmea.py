#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Hackerfleet Technology Demonstrator
# =====================================================================
# Copyright (C) 2011-2014 riot <riot@hackerfleet.org> and others.
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


__author__ = 'riot'

import time

from circuits import Component, Event
from pynmea.streamer import NMEAStream

class sensordata(Event):
    def __init__(self, data):
        super(sensordata, self).__init__()
        self.data = data

class NMEAParser(Component):
    """Parses raw data (e.g. from a serialport) for NMEA data and
    sends single sentences out.
    """

    channel = "nmea"

    def __init__(self):
        super(NMEAParser, self).__init__()
        self.streamer = NMEAStream()
        #self.streamer.get_objects("\n")

    def _parse(self, data):
        """
        Called when a publisher sends a new nmea sentence to this sensor.

        The nmea data is parsed and returned as NMEASentence object
        """
        #sentences = []
        sen_time = time.time()

        # TODO: Something here is fishy, as in the first received packet
        # gets lost in the NMEAStream object. WTF.
        # (That was possibly an Axon initialization issue and should be fixed now)

        for sentence in self.streamer.get_objects(data, size=len(data)+1):
            nmeadata = sentence.__dict__
            del(nmeadata['parse_map'])
            del(nmeadata['nmea_sentence'])
            nmeadata['time'] = sen_time
            nmeadata['type'] = sentence.sen_type
            #sentences.append(nmeadata)
            self.fireEvent(sensordata(nmeadata))

        #return sentences

    def read(self, *args, **kwargs):
        data = args
        self._parse(data)

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


Module NMEA
===========


"""

import time
import sys
import glob
import ais

from circuits import Component, Timer, Event
from circuits.net.sockets import TCPClient
from circuits.net.events import connect, read
from circuits.io.serial import Serial
from decimal import Decimal
from hfos.component import ConfigurableComponent, handler
from hfos.database import ValidationError
from hfos.logger import hfoslog, verbose, debug, warn, critical, error, hilight
from hfos.navdata.bus import register_protocol, start_scanner


# from pprint import pprint

class ais_position(Event):
    def __init__(self, bus, data, *args, **kwargs):
        super(ais_position, self).__init__(*args, **kwargs)
        self.bus = bus
        self.data = data


class AISParser(ConfigurableComponent):
    """
    Parses raw data (e.g. from a serialport) for AIS data and sends single
    sentences out.
    """

    configprops = {
        'auto_configure': {
            'type': 'boolean',
            'title': 'Auto configure',
            'description': 'Auto detect and configure serial device',
            'default': True
        }
    }

    channel = "ais"

    def __init__(self, *args, **kwargs):
        super(AISParser, self).__init__('AIS', *args, **kwargs)

        self.log("Started")

        self.unparsable = []

        self.fireEvent(register_protocol(self.channel, '!AIV'), 'serial')

    def raw_data(self, event):
        # self.log('Raw data received:', event.data)

        try:
            ais_data = event.data[1].split(',')[-2]
            parsed = ais.decode(ais_data, 0)
            self.log('Parsed ais data:', parsed, lvl=verbose)
            self.fireEvent(ais_position(bus=event.bus, data=parsed), 'ais')
        except Exception as e:
            self.log('Problem during parsing:', event.data[1], e, type(e),
                     exc=True, lvl=warn)
            self.unparsable += event

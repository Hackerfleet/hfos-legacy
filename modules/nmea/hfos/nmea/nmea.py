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


from decimal import Decimal
from hfos.component import ConfigurableComponent, handler
from hfos.logger import hfoslog, events, verbose, debug, warn, critical, error, hilight
from hfos.navdata.events import sensordata
from hfos.navdata.bus import register_protocol

from pprint import pprint


try:
    from pynmea2 import parse
except ImportError:
    parse = None
    hfoslog("No pynmea found, install requirements-optional.txt", lvl=warn,
            emitter="NMEA")


class NMEAParser(ConfigurableComponent):
    """
    Parses raw data (e.g. from a serialport) for NMEA data and sends single
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

    channel = "nmea0183"

    def __init__(self, *args, **kwargs):
        super(NMEAParser, self).__init__('NMEA', *args, **kwargs)

        if not parse:
            self.log("NOT started.", lvl=warn)
            return
        self.log("Started")

        self.unhandled = []
        self.unparsable = []

        # TODO: This only finds nmea busses with a connected GPS
        self.fireEvent(register_protocol(self.channel, '$'),
                       'serial')

    def _handle(self, sentence):
        try:
            sentence_fields = {}

            for item in sentence.fields:
                item_name = item[1]
                # self.log(item_name, lvl=critical)
                value = getattr(sentence, item_name)
                if value:
                    if len(item) == 3:
                        if item[2] in (Decimal, float):
                            value = float(value)
                        elif item[2] == int:
                            value = int(value)

                    sentence_fields.update({
                        sentence.sentence_type + '_' + item_name: value
                    })

            return sentence_fields
        except Exception as e:
            self.log("Error during handling: ", sentence, e, type(e),
                     lvl=error, exc=True)

    def raw_data(self, event):
        """Handles incoming raw sensor data
        :param event: Raw sentences incoming data
        """

        self.log('Received raw data from bus', lvl=events)
        if not parse:
            return

        nmea_time = event.data[0]
        try:
            parsed_data = parse(event.data[1])
        except Exception as e:
            self.log('Unparseable sentence:', event.data[1], e, type(e),
                     exc=True, lvl=warn)
            self.unparsable += event
            return

        bus = event.bus

        sensor_data_package = self._handle(parsed_data)

        self.log("Sensor data:", sensor_data_package, lvl=verbose)

        if sensor_data_package:
            # pprint(sensor_data_package)
            self.fireEvent(sensordata(sensor_data_package, nmea_time, bus),
                           "navdata")
            # self.log("Unhandled data: \n", self.unparsable, "\n",
            # self.unhandled, lvl=warn)


#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from circuits import Event
from hfos.logger import hfoslog, events
from hfos.events.system import authorizedevent

__license__ = """
Hackerfleet Operating System
============================
Copyright (C) 2011 - 2016 riot <riot@hackerfleet.org> and others.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# UI events


class navdatarequest(authorizedevent):
    def __init__(self, *args):
        super(navdatarequest, self).__init__(*args)
        hfoslog('Navdatarequest created:', args, emitter='NAVDATA', lvl=events)



# Internal Navigation Events

class sensordata(Event):
    """New sensordata has been parsed"""

    def __init__(self, data, timestamp, bus):
        """

        :param data: Parsed NMEA? Data
        """
        super(sensordata, self).__init__()
        self.data = data
        self.timestamp = timestamp
        self.bus = bus


class referenceframe(Event):
    """New sensordata has been parsed"""

    def __init__(self, data):
        """

        :param data: Parsed NMEA? Data
        """
        super(referenceframe, self).__init__()
        self.data = data
        hfoslog("[NAVDATA-EVENT] Reference frame generated: ", data,
                lvl=events)



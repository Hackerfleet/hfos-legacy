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

from circuits import Event
from hfos.logger import hfoslog, events
from hfos.events.system import authorizedevent


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


class updateposition(Event):
    """This vessel's position has been updated"""

    def __init__(self, vessel):
        """

        :param vessel: Vessel object (System Default Vessel)
        """
        super(updateposition, self).__init__()
        self.vessel = vessel
        hfoslog("[NAVDATA-EVENT] Vessel position has changed: ", vessel,
                lvl=events)


class updatevessel(Event):
    """Vessel has transmitted new coordinates"""

    def __init__(self, ship_id, coords, source, timestamp, data):
        """

        :param data: Parsed NMEA? Data
        """
        super(updatevessel, self).__init__()
        self.ship_id = ship_id
        self.source = source
        self.coords = coords
        self.data = data
        self.timestamp = timestamp

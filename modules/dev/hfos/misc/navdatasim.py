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

Module: Navdata Simulator
=========================

A controllable navdata event simulation utility


"""
from hfos.navdata.events import sensordata

from hfos.component import ConfigurableComponent
from hfos.logger import error, warn, verbose, hilight
from circuits import Timer, Event
from hfos.component import handler
from time import time
from random import randint


class generatenavdata(Event):
    pass


class NavdataSim(ConfigurableComponent):
    """
    Event Playback

    Produces
    * outgoing events, that have previously been recorded to a readable json
    file
    """

    configprops = {}

    def __init__(self, *args):
        super(NavdataSim, self).__init__("NAVSIM", *args)

        if self.config.active is True:
            self.log("Started, channel:", self.channel)
            Timer(3, generatenavdata(), persist=True).register(self)
        else:
            self.log("Disabled.")

    @handler('generatenavdata')
    def generatenavdata(self, *args):
        self.log('Sending out simulated package.', lvl=verbose)
        data = {'DBT_depth_meters': randint(1, 250)}
        event = sensordata(data, time(), 'SIM')
        self.fireEvent(event, 'navdata')

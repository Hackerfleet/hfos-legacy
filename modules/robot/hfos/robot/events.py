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

from circuits import Event


class machineroom_event(Event):
    """

    :param value:
    :param args:
    """

    def __init__(self, value, *args):
        super(machineroom_event, self).__init__(*args)
        self.controlvalue = value


class machine(machineroom_event):
    """Skipper wants us to change the engine speed/direction"""


class pump(machineroom_event):
    """Skipper wants us to turn on/off the coolant pump"""


class rudder(machineroom_event):
    """Skipper wants us to change the rudder angle"""


class control_update(Event):
    """A client wants to remote control a servo"""

    def __init__(self, controldata, *args):
        super(control_update, self).__init__(*args)
        self.controldata = controldata

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

Module: Event Recorder
======================

A controllable event recorder utility component


"""

from hfos.component import handler
from hfos.component import ConfigurableComponent
from hfos.events.system import authorizedevent
from hfos.logger import hilight  # , error, warn
from json import dumps
from time import time


class Recorder(ConfigurableComponent):
    """
    Event Recorder

    Handles
    * incoming events, that are recorded to a storable json file
    """

    configprops = {}

    def __init__(self, *args):
        super(Recorder, self).__init__("REC", *args)

        self.active = False

        if self.active:
            self.logfile = open('/tmp/hfos_recording', 'w')

            self.log("Started")

    @handler()
    def eventhandler(self, event, *args, **kwargs):
        if self.active and isinstance(event, authorizedevent):
            self.log("Recording event", lvl=hilight)
            # TODO: The event fields must be serialized to record everything
            #  in order. Component is deactivated until that can be done.
            data = dumps({time(): [event.user.uuid, event.action, event.data]})
            self.logfile.write(data)
            self.logfile.flush()

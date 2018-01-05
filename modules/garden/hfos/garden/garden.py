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


Module: Garden
==============


"""

from hfos.component import ConfigurableComponent
from hfos.logger import warn  # , hfoslog, error, critical


# from hfos.database import objectmodels
# from datetime import datetime
# from hfos.events.system import updatesubscriptions, send

class Garden(ConfigurableComponent):
    """
    The Garden component checks on the existing garden watering rules and
    triggers pump start/stop events accordingly. It also accepts interrupt
    notifications from authorized users to start/stop/suspend the watering
    plan.
    In future, it should also monitor weather and sensor data to water
    efficiently.
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the Garden component.

        :param args:
        """

        super(Garden, self).__init__("GARDEN", *args)

        self.log("Started")

    def gardenrequest(self, event):
        self.log("Someone interacts with the garden! Yay!", event, lvl=warn)

    def objectcreation(self, event):
        if event.schema == 'wateringrule':
            self.log("Reloading rules")
            self._reloadWateringRules()

    def _reloadWateringRules(self):
        """
        Reloads all stored watering rules.
        """
        self.log("No, not yet.")

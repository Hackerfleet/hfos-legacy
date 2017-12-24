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


Module: Calendar
================


"""

from hfos.component import ConfigurableComponent, handler
from hfos.database import objectmodels
from hfos.logger import debug, error
from hfos.events.system import authorizedevent
from hfos.events.client import send

# from pprint import pprint



class Manager(ConfigurableComponent):
    """
    Manages calendar resources.
    """
    channel = "hfosweb"

    configprops = {}

    def __init__(self, *args):
        """
        Initialize the CalendarWatcher component.

        :param args:
        """

        super(Manager, self).__init__("CALENDAR", *args)

        self.log("Started")

    def objectcreation(self, event):
        if event.schema == 'event':
            self.log("Updating calendar")

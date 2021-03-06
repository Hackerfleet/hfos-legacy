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


Module: Crewmanager
===================


"""

from hfos.component import ConfigurableComponent
from hfos.logger import warn  # , hfoslog, error, critical


# from hfos.database import objectmodels
# from datetime import datetime
# from hfos.events.system import updatesubscriptions, send


class Crewmanager(ConfigurableComponent):
    """
    The Crew component monitors crew changes. It does not do much.
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the Crew component.

        :param args:
        """

        super(Crewmanager, self).__init__("CREW", *args)

        self.log("Started")

    def crewrequest(self, event):
        self.log("Someone interacts with the crew! Yay!", event, lvl=warn)

    def objectcreation(self, event):
        if event.schema == 'crewconfig':
            self.log("Crewconfig was modified: ", event)

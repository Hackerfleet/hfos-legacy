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


Module: contactmanager
===================


"""

from hfos.component import ConfigurableComponent
from hfos.logger import warn  # , hfoslog, error, critical


# from hfos.database import objectmodels
# from datetime import datetime
# from hfos.events.system import updatesubscriptions, send


class contactmanager(ConfigurableComponent):
    """
    The contact component monitors contact changes. It does not do much.
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the contact component.

        :param args:
        """

        super(contactmanager, self).__init__("contact", *args)

        self.log("Started")

    def contactrequest(self, event):
        self.log("Someone interacts with the contact! Yay!", event, lvl=warn)

    def objectcreation(self, event):
        if event.schema == 'contactconfig':
            self.log("contactconfig was modified: ", event)

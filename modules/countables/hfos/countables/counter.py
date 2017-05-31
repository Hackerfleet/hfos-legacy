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


Module: Countables
==================


"""

from hfos.component import ConfigurableComponent, handler
from hfos.database import objectmodels
from hfos.logger import hfoslog, error, warn, critical, events
from hfos.events.system import authorizedevent
from pprint import pprint


class increment(authorizedevent):
    """Increments the counter of a countable object"""


class Counter(ConfigurableComponent):
    """
    Watches for incrementation requests.
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the CountableWatcher component.

        :param args:
        """

        super(Counter, self).__init__("COUNT", *args)

        self.log("Started")

    @handler(increment)
    def increment(self, event):
        self.log(event.user.account.name, "counted another object!",
                 event.data)
        countable = objectmodels['countable'].find_one({'uuid': event.data})
        try:
            countable.amount += 1
        except AttributeError:
            # Was not initialized yet
            countable.amount = 1
        countable.save()

    def objectcreation(self, event):
        if event.schema == 'countable':
            self.log("Updating countables")

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


Module: Nodestate
=================


"""

from circuits import Event

from hfos.component import ConfigurableComponent, handler, authorizedevent
from hfos.events.objectmanager import updatesubscriptions
from hfos.logger import warn, verbose
from hfos.database import objectmodels


class toggle(authorizedevent):
    pass


class backend_nodestate_toggle(Event):
    """Toggles a Nodestate from backend components"""

    def __init__(self, uuid, off=False, *args):
        super(backend_nodestate_toggle, self).__init__(*args)
        self.uuid = uuid
        self.off = off


class Nodestate(ConfigurableComponent):
    """
    The Nodestate component monitors nodestate changes. It does not do much.
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the Nodestate component.

        :param args:
        """

        super(Nodestate, self).__init__("NODESTATE", *args)

        self.nodestates = {}

        for item in objectmodels['nodestate'].find():
            self.nodestates[item.uuid] = item

        self.log("Started with", len(self.nodestates), "nodestate(s)")

    @handler(toggle)
    def nodestate_toggle(self, event):
        self.log("User toggle of a nodestate:", event, lvl=verbose)

        uuid = event.data

        self._toggle_state(uuid)

    @handler("backend_nodestate_toggle")
    def backend_nodestate_toggle(self, event):
        self.log("Backend toggle of a nodestate:", event, lvl=verbose)

        uuid = event.uuid
        self._toggle_state(uuid, off=event.off, force=True)

    def _toggle_state(self, uuid, off=False, force=False):
        state = self.nodestates[uuid]
        untrigger = []

        self.log('Trying to toggle state:', state, lvl=verbose)
        if off:
            state.active = True

        if state.active is True:
            state.active = False
            state.save()
            self.fire(updatesubscriptions('nodestate', state))
        elif state.active is False:
            for other, item in self.nodestates.items():
                if not force and (other in state.excluded and item.active is True):
                    self.log('Not triggering, that state is excluded by state:', self.nodestates[other].name,
                             lvl=warn)
                    return
                if item.active is True and other in state.untrigger:
                    untrigger.append(other)
            state.active = True

            state.save()
            self.fire(updatesubscriptions('nodestate', state))

        for item in untrigger:
            # TODO: Detect and break potential loops here
            self._toggle_state(item, off=True)

    def objectcreation(self, event):
        if event.schema == 'nodestate':
            self.log("NodeState was modified: ", event)

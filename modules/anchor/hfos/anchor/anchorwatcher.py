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


Module NMEA
===========


"""

from time import time
from circuits import Event
from vincenty import vincenty

from hfos.component import ConfigurableComponent, handler
from hfos.database import objectmodels
from hfos.logger import hfoslog, verbose, debug, warn, critical, error, hilight
from hfos.alert.manager import backend_trigger, backend_cancel, backend_notify
from hfos.debugger import cli_register_event
from hfos.nodestate.manager import backend_nodestate_toggle

# from pprint import pprint

STATE_UUID_ANCHORED = '121d5144-9ce0-499f-9378-556efdb6b451'
STATE_UUID_ADRIFT = '44c060b0-6002-4a40-9e88-6266918a813a'


class cli_trigger_anchorwatch(Event):
    pass


class AnchorWatcher(ConfigurableComponent):
    """
    When enabled, observes the NMEA bus for position updates and warns
    if the position has changed beyond a configured distance.

    TODO: Supply a geographic representation of the swinging circle to the map,
          This needs a bit of UI to set up, though!
    """

    # TODO: Maybe add a simpler interface to change the current limits, as they depend
    # on anchorage equipment in use each time.

    configprops = {
        'warn': {
            'type': 'integer',
            'title': 'Warning Distance',
            'description': 'First warning distance (meter)',
            'default': 10
        },
        'warn_timeout': {
            'type': 'integer',
            'title': 'Warning interval',
            'description': 'If condition persists, it will be repeated in this interval (s)',
            'default': 30
        },
        'alert': {
            'type': 'integer',
            'title': 'Alert Distance',
            'description': 'Final alerting distance (meter)',
            'default': 25
        },
        'role': {
            'type': 'string',
            'title': 'Roles',
            'description': 'User roles to alert',
            'default': 'all'
        }
    }

    def __init__(self, *args, **kwargs):
        super(AnchorWatcher, self).__init__('ANCHOR', *args, **kwargs)

        self.initial_position = None
        self.watching = False
        self.triggered = False
        self.last_warn = 0

        self.fireEvent(cli_register_event('aw_trigger', cli_trigger_anchorwatch))

        state = objectmodels['nodestate'].find_one({'uuid': STATE_UUID_ANCHORED})
        self._toggle(state.active)

        self.log("Started")

    def _toggle(self, state):
        self.last_warn = 0
        self.triggered = False
        self.initial_position = None
        self.watching = state
        if state is True:
            self.fireEvent(backend_cancel('Anchor Movement'))
        self.log('Anchorwatcher running:', self.watching)

    @handler("cli_trigger_anchorwatch")
    def cli_trigger_anchorwatch(self, event):
        self.log('Triggering anchorwatch alert')
        self.initial_position = [200.1, 200.1]

    @handler('updateposition')
    def updateposition(self, event):
        if self.watching is True and self.triggered is False:
            self.log('Updating position', lvl=verbose)
            current_position = event.vessel.geojson['coordinates']

            if self.initial_position is None:
                self.initial_position = current_position
                self.log('Initial position captured:', self.initial_position)
                return

            distance = vincenty(self.initial_position, current_position)

            if distance >= self.config.warn:
                if distance < self.config.alert:
                    if self.last_warn > 0 and time() < self.last_warn + self.config.warn_timeout:
                        return

                    self.last_warn = time()

                    self.log('Distance crossed alert threshold:', distance, lvl=warn)
                    s = 'The anchor has moved over the warn threshold (%im): %im' % (self.config.warn, distance)

                    self.fireEvent(backend_notify(
                        'warning', 'Anchor Movement', s,
                        self.config.role, self.config.warn_timeout
                    ))
                else:
                    self.log('Distance crossed warning threshold:', distance, lvl=warn)
                    self.triggered = True

                    self.fireEvent(backend_nodestate_toggle(STATE_UUID_ADRIFT))

                    alert = {
                        'topic': 'Anchor Movement',
                        'message': 'The anchor has moved over the alert threshold (%im): %im' % (
                            self.config.alert, distance),
                        'role': self.config.role
                    }
                    self.fireEvent(backend_trigger(alert))

    @handler('updatesubscriptions')
    def updatesubscriptions(self, event, *args):
        if event.schema == 'nodestate':
            data = event.data
            if data.uuid == STATE_UUID_ANCHORED:
                self._toggle(data.active)

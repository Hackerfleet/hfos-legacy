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


Module: AutomatWatcher
======================


"""

from hfos.component import ConfigurableComponent, authorizedevent, handler
from hfos.events.client import send
from hfos.events.objectmanager import objectcreation, objectchange, \
    objectdeletion
from circuits import Event, Timer
from hfos.logger import warn, error, critical, hilight, debug
from copy import deepcopy
import json
from hfos.database import objectmodels


# from datetime import datetime
# from hfos.events.system import updatesubscriptions, send


class store_rule(authorizedevent):
    """User requests to store a rule"""


class get_events(authorizedevent):
    """Requests a list of automatable events"""


class rule_reload(Event):
    pass


class rule_triggered(Event):
    """An established rule has been triggered"""

    def __init__(self, *args):
        """
        """
        super(rule_triggered, self).__init__(*args)


class Manager(ConfigurableComponent):
    """
    The Automat Manager component monitors automat rule changes. It does not
    do much.
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the Automat Manager component.

        :param args:
        """

        super(Manager, self).__init__("AUTOMAT", *args)

        self.authorized_events = None
        self.rules = {}
        self.updating = False

        self.log("Started")

    @handler("objectcreation")
    def objectcreation(self, event):
        self.on_rule_change(event)

    @handler("objectdeletion")
    def objectdeletion(self, event):
        self.on_rule_change(event)

    @handler("objectchange")
    def objectchange(self, event):
        self.on_rule_change(event)

    def on_rule_change(self, event):
        if event.schema == 'automatrule':
            self.log('Storage of automat rule requested, updating rules')
            if not self.updating:
                Timer(2, rule_reload(), persist=False).register(self)
                self.updating = True

    @handler(get_events)
    def get_events(self, event):
        self.log('Automatable event list requested:', event.user.account.name)

        events = deepcopy(self.authorized_events)

        for source in events:
            for value in events[source].values():
                del (value['event'])

        packet = {
            'component': 'hfos.automat.manager',
            'action': 'get_events',
            'data': events
        }
        self.fireEvent(send(event.client.uuid, packet))

    def ready(self, event):
        from hfos.events.system import AuthorizedEvents
        self.authorized_events = AuthorizedEvents
        self.log('Automat Started.')
        self.log('Event sources:', AuthorizedEvents.keys(), lvl=debug)
        self._load_rules()

    @handler("rule_reload")
    def _load_rules(self):
        for rule in objectmodels['automatrule'].find({'enabled': True}):
            name = rule.input['event']['source'] + '.' + rule.input[
                'event']['name']
            self.rules[name] = rule

        self.updating = False
        self.log('%i Automat rules activated' % len(self.rules))

    def _react(self, rule):
        output = rule.output

        args = json.loads(output.data)
        dest = output['event']['destination']
        name = output['event']['name']
        event = self.authorized_events[dest][name]['event'](**args)

        self.log('Firing automated event:', event.__dict__)
        self.fireEvent(event, 'hfosweb')

    def _compare_int(self, arg, data, func):
        if func == 'equals':
            if data == arg:
                return True
        elif func == 'lower':
            if data < arg:
                return True
        elif func == 'lower_equals':
            if data <= arg:
                return True
        elif func == 'bigger_equals':
            if data >= arg:
                return True
        elif func == 'bigger':
            if data > arg:
                return True
        return False

    @handler(channel="*")
    def eventhandler(self, event, *args, **kwargs):
        if event.name in self.rules:
            self.log('Input rule triggered!', lvl=hilight)
            logic = self.rules[event.name].input['logic']

            try:
                for rule in logic:
                    arg = rule['argument']
                    func = rule['function']
                    tool = rule['tool']
                    field = rule['field']

                    data = getattr(event, field)

                    if tool == 'compare_int':
                        data = int(data)
                        arg = int(arg)
                        if self._compare_int(arg, data, func):
                            self._react(rule)
            except Exception as e:
                self.log('Automat broke down:', e, type(e), exc=True)

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

Module: SchemaManager
=====================


"""

from circuits import Event

from hfos.events.client import send
from hfos.events.schemamanager import get, all, configuration
from hfos.debugger import cli_register_event
from hfos.component import ConfigurableComponent
from hfos.database import schemastore, configschemastore
from hfos.logger import warn, debug  # , error, hilight
from hfos.component import handler


class cli_schemata(Event):
    pass


class cli_form(Event):
    pass


class SchemaManager(ConfigurableComponent):
    """
    Handles schemata requests from clients.
    """

    channel = "hfosweb"

    configprops = {}

    def __init__(self, *args):
        super(SchemaManager, self).__init__('SM', *args)

        self.fireEvent(cli_register_event('schemata', cli_schemata))
        self.fireEvent(cli_register_event('form', cli_form))

    @handler('cli_schemata')
    def cli_schemata_list(self, *args):
        """Prints a list of registered schemata"""

        self.log('Registered Schemata:', ",".join(sorted(schemastore.keys())), pretty=True)
        if 'CONFIG' in args:
            self.log('Registered Configuration Schemata:', ",".join(sorted(configschemastore.keys())), pretty=True)

    @handler('cli_form')
    def cli_form(self, *args):
        self.log(schemastore[args[0]]['form'], pretty=True)

    @handler('ready')
    def ready(self):
        """Sets up the application after startup."""
        self.log('Got', len(schemastore), 'data and',
                 len(configschemastore), 'component schemata.', lvl=debug)

        # pprint(schemastore.keys())
        # pprint(configschemastore.keys())

    @handler(all)
    def all(self, event):
        """Return all known schemata to the requesting client"""

        self.log("Schemarequest for all schemata from",
                 event.user, lvl=debug)
        response = {
            'component': 'hfos.events.schemamanager',
            'action': 'all',
            'data': schemastore
        }
        self.fireEvent(send(event.client.uuid, response))

    @handler(get)
    def get(self, event):
        """Return a single schema"""
        self.log("Schemarequest for", event.data, "from",
                 event.user, lvl=debug)
        if event.data in schemastore:
            response = {
                'component': 'hfos.events.schemamanager',
                'action': 'get',
                'data': schemastore[event.data]
            }
            self.fireEvent(send(event.client.uuid, response))
        else:
            self.log("Unavailable schema requested!", lvl=warn)

    @handler(configuration)
    def configuration(self, event):
        """Return all configurable components' schemata"""

        try:
            self.log("Schemarequest for all configuration schemata from",
                     event.user.account.name, lvl=debug)
            response = {
                'component': 'hfos.events.schemamanager',
                'action': 'configuration',
                'data': configschemastore
            }
            self.fireEvent(send(event.client.uuid, response))
        except Exception as e:
            self.log("ERROR:", e)

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

Module: SchemaManager
=====================


"""

from hfos.events.client import send
from hfos.events.schemamanager import get, all, configuration
from hfos.component import ConfigurableComponent
from hfos.database import schemastore, configschemastore
from hfos.logger import error, warn, debug, hilight
from hfos.component import handler


class SchemaManager(ConfigurableComponent):
    """
    Handles schemata requests from clients.
    """

    channel = "hfosweb"

    configprops = {}

    def __init__(self, *args):
        super(SchemaManager, self).__init__('SM', *args)

    @handler('ready')
    def ready(self):
        """Sets up the application after startup."""
        self.log('Got', len(schemastore), 'data and',
                 len(configschemastore), 'component schemata.')

        # pprint(schemastore.keys())
        # pprint(configschemastore.keys())

    @handler(all)
    def all(self, event):
        self.log("Schemarequest for all schemata from",
                 event.user.account.name)
        response = {
            'component': 'hfos.events.schemamanager',
            'action': 'all',
            'data': schemastore
        }
        self.fireEvent(send(event.client.uuid, response))

    @handler(get)
    def get(self, event):
        self.log("Schemarequest for", event.data, "from",
                 event.user.account.name)
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
        try:
            self.log("Schemarequest for all configuration schemata from",
                     event.user.account.name)
            response = {
                'component': 'hfos.events.schemamanager',
                'action': 'configuration',
                'data': configschemastore
            }
            self.fireEvent(send(event.client.uuid, response))
        except Exception as e:
            self.log("ERROR:", e)

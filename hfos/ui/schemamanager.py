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
from hfos.database import schemastore, l10n_schemastore, configschemastore
from hfos.logger import warn, debug, error  # , hilight
from hfos.component import handler


class cli_schema(Event):
    """Display a specified schema"""
    pass


class cli_schemata(Event):
    """Display all registered schemata"""
    pass


class cli_form(Event):
    """Display a specified form"""
    pass


class cli_forms(Event):
    """List all registered forms"""
    pass


class cli_default_perms(Event):
    """Display all schemata default permission roles"""
    pass


class SchemaManager(ConfigurableComponent):
    """
    Handles schemata requests from clients.
    """

    channel = "hfosweb"

    configprops = {}

    def __init__(self, *args):
        super(SchemaManager, self).__init__('SM', *args)

        self.fireEvent(cli_register_event('schema', cli_schema))
        self.fireEvent(cli_register_event('schemata', cli_schemata))
        self.fireEvent(cli_register_event('form', cli_form))
        self.fireEvent(cli_register_event('forms', cli_forms))
        self.fireEvent(cli_register_event('permissions_default', cli_default_perms))

    @handler('cli_schemata')
    def cli_schemata_list(self, *args):
        """Display a list of registered schemata"""

        self.log('Registered schemata languages:', ",".join(sorted(l10n_schemastore.keys())))
        self.log('Registered Schemata:', ",".join(sorted(schemastore.keys())))
        if 'CONFIG' in args:
            self.log('Registered Configuration Schemata:', ",".join(sorted(configschemastore.keys())), pretty=True)

    @handler('cli_form')
    def cli_form(self, *args):
        """Display a schemata's form definition"""

        if args[0] == '*':
            for schema in schemastore:
                self.log(schema, ':', schemastore[schema]['form'], pretty=True)
        else:
            self.log(schemastore[args[0]]['form'], pretty=True)

    @handler('cli_schema')
    def cli_schema(self, *args):
        """Display a single schema definition"""

        key = None
        if len(args) > 1:
            key = args[1]

        def output(schema):
            self.log("%s :" % schema)
            if key == 'props':
                self.log(schemastore[schema]['schema']['properties'], pretty=True)
            elif key == 'perms':
                try:
                    self.log(schemastore[schema]['schema']['roles_create'], pretty=True)
                except KeyError:
                    self.log('Schema', schema, 'has no role for creation', lvl=warn)
                try:
                    self.log(schemastore[schema]['schema']['properties']['perms']['properties'], pretty=True)
                except KeyError:
                    self.log('Schema', schema, 'has no permissions', lvl=warn)
            else:
                self.log(schemastore[schema]['schema'], pretty=True)

        if args[0] == '*':
            for schema in schemastore:
                output(schema)
        else:
            output(args[0])

    @handler('cli_forms')
    def cli_forms(self, *args):
        """List all available form definitions"""

        forms = []
        missing = []

        for key, item in schemastore.items():
            if 'form' in item and len(item['form']) > 0:
                forms.append(key)
            else:
                missing.append(key)

        self.log('Schemata with form:', forms)
        self.log('Missing forms:', missing)

    @handler('cli_default_perms')
    def cli_default_perms(self, *args):
        """Show default permissions for all schemata"""

        for key, item in schemastore.items():
            # self.log(item, pretty=True)
            if item['schema'].get('no_perms', False):
                self.log('Schema without permissions:', key)
                continue
            try:
                perms = item['schema']['properties']['perms']['properties']
                if perms == {}:
                    self.log('Schema:', item, pretty=True)

                self.log(
                    'Schema:', key,
                    'read', perms['read']['default'],
                    'write', perms['write']['default'],
                    'list', perms['list']['default'],
                    'create', item['schema']['roles_create']
                )
            except KeyError as e:
                self.log('Fishy schema found:', key, e, lvl=error)
                self.log(item, pretty=True)

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
            'data': l10n_schemastore[event.client.language]
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
                'data': l10n_schemastore[event.client.language][event.data]
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

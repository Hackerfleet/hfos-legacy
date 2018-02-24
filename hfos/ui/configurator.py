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

Module: Configurator
=====================


"""

from hfos.events.client import send
from hfos.component import ConfigurableComponent, authorizedevent, handler
from hfos.schemata.component import ComponentConfigSchemaTemplate as Schema
from hfos.database import ValidationError
from hfos.logger import error, warn
from warmongo import model_factory

try:
    PermissionError
except NameError:  # pragma: no cover
    class PermissionError(Exception):
        """Not enough Permissions (2to3 substitute)"""
        pass


class getlist(authorizedevent):
    """A client requires a schema to validate data or display a form"""

    roles = ['admin']


class get(authorizedevent):
    """A client requires a schema to validate data or display a form"""

    roles = ['admin']


class put(authorizedevent):
    """A client requires a schema to validate data or display a form"""

    roles = ['admin']


class Configurator(ConfigurableComponent):
    """
    Provides a common configuration interface for all HFOS components.

    (You're probably looking at it right now)
    """

    channel = "hfosweb"

    configprops = {}

    def __init__(self, *args):
        super(Configurator, self).__init__('CONF', *args)

    @handler(getlist)
    def getlist(self, event):
        """Processes configuration list requests

        :param event:
        """

        try:

            componentlist = model_factory(Schema).find({})
            data = []
            for comp in componentlist:
                data.append({
                    'name': comp.name,
                    'uuid': comp.uuid,
                    'class': comp.componentclass,
                    'active': comp.active
                })

            data = sorted(data, key=lambda x: x['name'])

            response = {
                'component': 'hfos.ui.configurator',
                'action': 'getlist',
                'data': data
            }
            self.fireEvent(send(event.client.uuid, response))
            return
        except Exception as e:
            self.log("List error: ", e, type(e), lvl=error, exc=True)

    @handler(put)
    def put(self, event):
        """Store a given configuration"""

        self.log("Configuration put request ",
                 event.user)

        try:
            component = model_factory(Schema).find_one({
                'uuid': event.data['uuid']
            })

            component.update(event.data)
            component.save()

            response = {
                'component': 'hfos.ui.configurator',
                'action': 'put',
                'data': True
            }
            self.log('Updated component configuration:',
                     component.name)
        except (KeyError, ValueError, ValidationError, PermissionError) as e:
            response = {
                'component': 'hfos.ui.configurator',
                'action': 'put',
                'data': False
            }
            self.log('Storing component configuration failed: ',
                     type(e), e, exc=True, lvl=error)

        self.fireEvent(send(event.client.uuid, response))
        return

    @handler(get)
    def get(self, event):
        """Get a stored configuration"""

        try:
            comp = event.data['uuid']
        except KeyError:
            comp = None

        if not comp:
            self.log('Invalid get request without schema or component',
                     lvl=error)
            return

        self.log("Config data get  request for ", event.data, "from",
                 event.user)

        component = model_factory(Schema).find_one({
            'uuid': comp
        })
        response = {
            'component': 'hfos.ui.configurator',
            'action': 'get',
            'data': component.serializablefields()
        }
        self.fireEvent(send(event.client.uuid, response))

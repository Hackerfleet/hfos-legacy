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

Module: TagManager
=====================


"""

from circuits import Timer, Event

from hfos.events.client import send
from hfos.events.schemamanager import get, all, configuration
from hfos.component import ConfigurableComponent
from hfos.database import objectmodels
from hfos.logger import warn, debug  # , error, hilight
from hfos.component import handler


class TagManager(ConfigurableComponent):
    """
    Handles schemata requests from clients.
    """

    channel = "hfosweb"

    configprops = {}

    def __init__(self, *args):
        super(TagManager, self).__init__('TM', *args)

        self.tags = {}

        tag = objectmodels['tag']

        for item in tag.find():
            self.tags[item.name] = item

        self.log('Tags:', self.tags, pretty=True, lvl=debug)

        #tagged = self._get_tagged('PR')

        #for item in tagged:
        #    self.log("Found tagged items:", item.serializablefields(), pretty=True)
        #Timer(3, Event.create('getTagged', 'PR')).register(self)

    #@handler('getTagged')
    def _get_tagged(self, tag):
        tag = self.tags[tag]
        self.log('TAG UUID', tag.uuid)
        tagged = []
        for model in objectmodels.values():
            self.log(model ,pretty=True)
            self.log('Find:', model.find, pretty=True)
            for item in model.find({'tags': {'uuid': tag.uuid}}):
                tagged.append(item)

        return tagged

    @handler(get)
    def get_tagged(self, event):
        """Return a single schema"""
        self.log("Tagged objects request for", event.data, "from",
                 event.user, lvl=debug)
        if event.data in self.tags:
            tagged = self._get_tagged(event.data)

            response = {
                'component': 'hfos.events.schemamanager',
                'action': 'get',
                'data': tagged
            }
            self.fireEvent(send(event.client.uuid, response))
        else:
            self.log("Unavailable schema requested!", lvl=warn)


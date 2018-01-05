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

Module: Wiki
============

Wiki manager


"""

from uuid import uuid4
from hfos.component import ConfigurableComponent
from hfos.logger import error, warn
from hfos.events.client import send
from hfos.database import ValidationError, objectmodels
import pymongo


# TODO: Currently unused:
# try:
#     from docutils.core import publish_parts
# except ImportError:
#     publish_parts = None
#     hfoslog("No docutils found! Install it to get full functionality!",
#             lvl=warn, emitter="WIKI")


class Wiki(ConfigurableComponent):
    """
    Wiki manager

    Handles
    * incoming page requests and updates
    * a list of registered pagenames
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(Wiki, self).__init__('WIKI', *args)

        self.log("Started")

    def objectcreation(self, event):
        self._page_update(event)

    def objectchange(self, event):
        self._page_update(event)

    def _page_update(self, event):
        """
        Checks if the newly created object is a wikipage..
        If so, rerenders the automatic index.

        :param event: objectchange or objectcreation event
        """
        try:
            if event.schema == 'wikipage':
                self._update_index()

        except Exception as e:
            self.log("Page creation notification error: ", event, e,
                     type(e), lvl=error)

    def _update_index(self):
        self.log('Updating page index')
        wikipage = objectmodels['wikipage']
        index = wikipage.find_one({'name': 'Index'})
        index.html = "<ul>"
        for item in wikipage.find(sort=[("name", pymongo.DESCENDING)]):
            try:
                title = item.title

                if title.startswith('#'):
                    continue
            except AttributeError:
                title = item.name
            index.html += '<li><a href="#!/wiki/' + item.name + '">' + \
                          title + '</a></li>'
        index.save()

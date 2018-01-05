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

Module: Chat
============

Chat manager


"""


from hfos.component import ConfigurableComponent, handler
from hfos.logger import error, warn, hilight, debug, verbose
from hfos.events.client import broadcast, send

from hfos.chat.host import say


class Bot(ConfigurableComponent):
    """
    Chat bot with NLP interface

    Handles
    * incoming chat messages
    * responding to various requests
    """

    configprops = {
        'name': {
            'type': 'string',
            'title': 'Name',
            'description': 'Name of this chat bot',
            'default': 'Hal'
        }
    }
    channel = "hfosweb"

    def __init__(self, *args):
        super(Bot, self).__init__("CHATBOT", *args)

        self.log("Started")

    @handler(say)
    def say(self, event):
        """Chat event handler for incoming events
        :param event: say-event with incoming chat message
        """

        try:
            userid = event.user.uuid
            recipient = self._get_recipient(event)
            content = self._get_content(event)

            if self.config.name in content:
                self.log('I think, someone mentioned me:', content)

        except Exception as e:
            self.log("Error: '%s' %s" % (e, type(e)), exc=True, lvl=error)

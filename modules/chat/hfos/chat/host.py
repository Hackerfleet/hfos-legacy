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

Module: Chat
============

Chat manager


"""

from time import time
from hfos.component import ConfigurableComponent, handler
from hfos.logger import error, warn
from hfos.events.client import broadcast
from hfos.events.system import authorizedevent

try:
    # noinspection PyDeprecation
    from cgi import escape
except ImportError:
    # noinspection PyCompatibility
    from html import escape


# Chat events


class say(authorizedevent):
    """A new chat event has been generated by the client"""


# Components


class Host(ConfigurableComponent):
    """
    Chat manager

    Handles
    * incoming chat messages
    * chat broadcasts
    """

    configprops = {}
    channel = "hfosweb"

    def __init__(self, *args):
        super(Host, self).__init__("CHAT", *args)

        self.log("Started")

    def _get_username(self, event):
        try:
            try:
                username = event.user.profile.nick
            except AttributeError:
                self.log("Nickname not found.")
                username = event.user.account.name

            try:
                username += "@" + event.client.config.name
            except AttributeError:
                self.log("Client name not found.")
                raise AttributeError

        except AttributeError:
            self.log("Couldn't find user- or clientname: ",
                     event.user.profile.to_dict(),
                     event.client.config.to_dict(), lvl=warn)
            username = "NO USERNAME"
        return username

    @handler(say)
    def say(self, event):
        """Chat event handler for incoming events
        :param event: say-event with incoming chat message
        """

        try:
            data = event.data
            username = self._get_username(event)

            # noinspection PyDeprecation
            msg = escape(str(data))
            msg = msg.replace('\n', '<br \>')

            chat_packet = {
                'component': 'hfos.chat.host',
                'action': 'broadcast',
                'data': {
                    'sender': username,
                    'timestamp': time(),
                    'content': msg
                }
            }

            try:
                self.fireEvent(broadcast("users", chat_packet))
            except Exception as e:
                self.log("Transmission error before broadcast: %s" % e,
                         lvl=error)

        except Exception as e:
            self.log("Error: '%s' %s" % (e, type(e)), lvl=error)
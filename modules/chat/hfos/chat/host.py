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

from time import time
from collections import namedtuple
from hfos.component import ConfigurableComponent, handler
from hfos.logger import error, warn, hilight, debug, verbose
from hfos.database import objectmodels
from hfos.events.client import broadcast, send
from hfos.events.system import authorizedevent
from hfos.tools import std_now, std_uuid, std_table
from circuits import Event
from pymongo import DESCENDING

from hfos.debugger import cli_register_event

try:
    # noinspection PyDeprecation
    from cgi import escape
except ImportError:
    # noinspection PyCompatibility
    from html import escape


# Chat events


class say(authorizedevent):
    """A new chat event has been generated by the client"""


class join(authorizedevent):
    """A new chat event has been generated by the client"""


class change(authorizedevent):
    """A new chat event has been generated by the client"""


class history(authorizedevent):
    """A new chat event has been generated by the client"""


# CLI events

class cli_user_list(Event):
    """Display current chat users"""
    pass


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

        chat_channels = {}

        for channel in objectmodels['chatchannel'].find():
            chat_channels[channel.uuid] = channel

        self.chat_channels = chat_channels
        self.users = {}
        self.user_attention = {}
        self.user_joins = {}
        self.clients = {}

        self.lastlogs = {}

        for userlog in objectmodels['chatlastlog'].find():
            self.lastlogs[userlog.owner] = userlog

        self.fireEvent(cli_register_event('chat_users', cli_user_list))
        self.log("Started")

    @handler("cli_user_list")
    def cli_user_list(self, *args):
        #self.log('Logged in users:', self.users, pretty=True)
        Row = namedtuple("User", ['Name', 'Attention'])
        rows = []
        for user in self.users.values():
            rows.append(Row(user.name, self.user_attention[user.uuid]))

        table = std_table(rows)
        self.log("Users:\n", table)

    def _get_recipient(self, event):
        try:
            recipient = event.data['recipient']
        except (AttributeError, TypeError) as e:
            self.log('Invalid chat message without recipient received',
                     e, type(e), event.data, lvl=error, exc=True, pretty=True)
            raise AttributeError
        return recipient

    def _get_content(self, event):

        # noinspection PyDeprecation
        msg = escape(str(event.data['content']))
        msg = msg.replace('\n', '<br \>')

        return msg

    def objectcreation(self, event):
        pass
        #self.log('Creation event!')

    @handler('clientdisconnect')
    def clientdisconnect(self, event):
        if event.clientuuid in self.clients:
            self.log('Logging out client:', event.clientuuid, lvl=debug)
            self.clients.pop(event.clientuuid)

    @handler("userlogout")
    def userlogout(self, event):
        self.log('Logging out user:', event.useruuid, lvl=debug)
        self.users.pop(event.useruuid)
        self.user_attention.pop(event.useruuid)

    @handler("userlogin")
    def userlogin(self, event):
        """Provides the newly authenticated user with a backlog and general
        channel status information"""

        try:
            user_uuid = event.useruuid
            user = objectmodels['user'].find_one({'uuid': user_uuid})

            if user_uuid not in self.lastlogs:
                self.log('Setting up lastlog for a new user.', lvl=debug)
                lastlog = objectmodels['chatlastlog']({
                    'owner': user_uuid,
                    'uuid': std_uuid(),
                    'channels': {}
                })
                lastlog.save()
                self.lastlogs[user_uuid] = lastlog

            self.users[user_uuid] = user
            self.user_attention[user_uuid] = None
            self._send_status(user_uuid, event.clientuuid)
        except Exception as e:
            self.log('Error during chat setup of user:', e, type(e), exc=True)

    def _get_unread(self, user):
        unread = {}

        user_query = {
            'users': {
                '$in': [user]
            }
        }
        try:
            for channel in objectmodels['chatchannel'].find(user_query):
                if channel.uuid not in self.lastlogs[user].channels:
                    lastlog_entry = 0
                else:
                    lastlog_entry = self.lastlogs[user].channels[channel.uuid]

                lastlog_query = {
                    'recipient': channel.uuid,
                    'timestamp': {'$gt': lastlog_entry}
                }
                unread[channel.uuid] = objectmodels['chatmessage'].count(
                    lastlog_query
                )

            return unread
        except Exception as e:
            self.log('Could not get unread counters:', e, type(e), exc=True,
                     lvl=error)

    def _send_status(self, user_uuid, client_uuid=None):
        try:
            joined = []
            for uuid, channel in self.chat_channels.items():
                if user_uuid in channel.users:
                    joined.append(uuid)

            unread = self._get_unread(user_uuid)

            self.log('User joined:', joined, ' and has unread:', unread,
                     pretty=True, lvl=debug)

            packet = {
                'component': 'hfos.chat.host',
                'action': 'status',
                'data': {
                    'joined': joined,
                    'unread': unread
                }
            }

            if not client_uuid:
                uuid = user_uuid
                sendtype = 'user'
            else:
                uuid = client_uuid
                sendtype = 'client'

            self.fireEvent(send(uuid, packet, sendtype=sendtype))

        except Exception as e:
            self.log('Error', e, type(e), lvl=error, exc=True)

    @handler(change)
    def change(self, event):
        self.log('Initiating channel change', lvl=debug)
        try:
            uuid = event.data
            user = event.user.uuid
            if user in self.users:
                if uuid in self.chat_channels:
                    self.user_attention[user] = uuid
                    self.update_lastlog(user, uuid)
                    self._send_status(user)
                else:
                    self.log('User switched to unknown channel', lvl=warn)
            else:
                self.log('Unknown user switch channels', lvl=warn)
        except Exception as e:
            self.log('Unknown channel change error:', e, type(e), exc=True)

    @handler(join)
    def join(self, event):
        """Chat event handler for incoming events
        :param event: say-event with incoming chat message
        """

        try:
            channel_uuid = event.data
            user_uuid = event.user.uuid

            if channel_uuid in self.chat_channels:
                self.log('User joins a known channel', lvl=debug)
                if user_uuid in self.chat_channels[channel_uuid].users:
                    self.log('User already joined', lvl=warn)
                else:
                    self.chat_channels[channel_uuid].users.append(user_uuid)
                    self.chat_channels[channel_uuid].save()
                    packet = {
                        'component': 'hfos.chat.host',
                        'action': 'join',
                        'data': channel_uuid
                    }
                    self.fireEvent(send(event.client.uuid, packet))
            else:
                self.log('Request to join unavailable channel', lvl=warn)
        except Exception as e:
            self.log('Join error:', e, type(e), exc=True, lvl=error)

    def update_lastlog(self, user, recipient):
        if self.user_attention[user] == recipient:
            self.log('Updating lastlog', lvl=debug)

            lastlog = self.lastlogs[user]

            lastlog.channels[recipient] = std_now()
            lastlog.save()
        else:
            self.log('Sending status update', lvl=debug)
            self._send_status(user)

    @handler(history)
    def history(self, event):
        try:
            channel = event.data['channel']
            limit = event.data['limit']
            end = event.data['end']
        except (KeyError, AttributeError) as e:
            self.log('Error during event lookup:', e, type(e), exc=True,
                     lvl=error)
            return

        self.log('History requested:', channel, limit, end, lvl=debug)

        messages = []

        om = objectmodels['chatmessage']
        try:
            for msg in om.find(
                    {
                        'recipient': channel,
                        'timestamp': {'$lte': end}
                    },
                    sort=[('timestamp', -1)],
                    limit=limit
            ):
                messages.insert(0, msg.serializablefields())
        except Exception as e:
            self.log('Error during history lookup:', e, type(e), exc=True,
                     lvl=error)
            return

        history_packet = {
            'component': 'hfos.chat.host',
            'action': 'history',
            'data': {
                'channel': channel,
                'limit': limit,
                'end': end,
                'history': messages
            }
        }
        self.fireEvent(send(event.client.uuid, history_packet))

    @handler(say)
    def say(self, event):
        """Chat event handler for incoming events
        :param event: say-event with incoming chat message
        """

        try:
            userid = event.user.uuid
            recipient = self._get_recipient(event)
            content = self._get_content(event)

            message = objectmodels['chatmessage']({
                'timestamp': time(),
                'recipient': recipient,
                'sender': userid,
                'content': content,
                'uuid': std_uuid()
            })

            message.save()

            chat_packet = {
                'component': 'hfos.chat.host',
                'action': 'say',
                'data': message.serializablefields()
            }

            if recipient in self.chat_channels:
                for useruuid in self.users:
                    if useruuid in self.chat_channels[recipient].users:
                        self.log('User in channel', lvl=debug)
                        self.update_lastlog(useruuid, recipient)

                        self.log('Sending message', lvl=debug)
                        self.fireEvent(send(useruuid, chat_packet,
                                            sendtype='user'))

        except Exception as e:
            self.log("Error: '%s' %s" % (e, type(e)), exc=True, lvl=error)

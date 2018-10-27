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

from random import randint
from socket import gethostname
from collections import defaultdict

from hfos.debugger import cli_register_event
from hfos.misc import std_hash, std_uuid
from hfos.component import ConfigurableComponent
from hfos.logger import error, warn, hilight, debug, verbose

from circuits import Timer, handler
from circuits.core.events import Event

from circuits.io import write, close

from circuits.net.events import connect, disconnect
from circuits.net.sockets import TCPClient

from circuits.protocols.irc import ERR_NICKNAMEINUSE
from circuits.protocols.irc import IRC, JOIN, USER, NICK, PRIVMSG
from circuits.protocols.irc import RPL_ENDOFMOTD, ERR_NOMOTD


class cli_test_irc_send(Event):
    """Test irc message transmission"""
    pass


class send_irc_message(Event):
    """Transmit a irc message to a user"""

    def __init__(self, username, subject, body, msg_type='query', *args, **kwargs):
        super(send_irc_message, self).__init__(*args, **kwargs)
        self.msg_type = msg_type
        self.body = body
        self.subject = subject
        self.username = username


class IRCGate(ConfigurableComponent):
    """
    IRC gateway for claptrap

    Handles
    * incoming irc  messages
    * irc roster changes
    * responding to various requests
    """

    configprops = {
        'host': {
            'title': 'Hostname',
            'description': 'IRC server host name',
            'default': 'irc.freenode.org'
        },
        'port': {
            'type': 'integer',
            'title': 'Port',
            'description': 'Port for this server',
            'default': 6667
        },
        'nick': {
            'type': 'string',
            'title': 'Nick',
            'description': 'Name on this server',
            'default': 'claptrap'
        },
        'password': {
            'type': 'string',
            'title': 'Password',
            'description': 'Nickserv password for this server',
        },
        'channels': {
            'type': 'array',
            'default': [
                {
                    'name': '#hackerfleet',
                }
            ],
            'items': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'title': 'Channel name',
                        'description': 'Name of the irc channel to join'
                    },
                    'key': {
                        'title': 'Join Key',
                        'type': 'string'
                    }
                }
            }
        }
    }

    def __init__(self, *args):
        ConfigurableComponent.__init__(self, "IRCBOT", *args)
        if self.config.get('password', None) is None:
            self.config.password = std_uuid()
            self.config.save()

        self.channel = 'ircbot'

        self.fireEvent(cli_register_event('test_irc_send', cli_test_irc_send), "hfosweb")
        self.log("Started")

        self.host = self.config.host
        self.port = self.config.port

        self.hostname = gethostname()

        self.nick = self.config.nick
        self.irc_channels = self.config.channels

        # Mapping of IRC Channel -> Set of Nicks
        self.channel_map = defaultdict(set)

        # Mapping of Nick -> Set of IRC Channels
        self.nick_map = defaultdict(set)

        # Add TCPClient and IRC to the system.
        self.transport = TCPClient(channel=self.channel).register(self)
        self.protocol = IRC(channel=self.channel).register(self)

        # Keep-Alive Timer
        Timer(60, Event.create("keepalive"), persist=True).register(self)

    def ready(self, component):
        """Ready Event
        This event is triggered by the underlying ``TCPClient`` Component
        when it is ready to start making a new connection.
        """

        self.fire(connect(self.host, self.port), 'ircbot')

    @handler('cli_test_irc_send', channel='hfosweb')
    def cli_test_irc_send(self, *args):
        """Tests IRC message sending"""

        self.log('Testing IRC message sending')
        self.fireEvent(send_irc_message('riot', 'Testing', 'This is a test message'))
        self.fireEvent(send_irc_message('#hackerfleet', 'Testing', 'Eek, that tickles! Stop it!'))

    def _message(self, msg):
        """The bot received a direct message"""

        self.log('Message received:', msg['body'], pretty=True)

        if msg['type'] in ('chat', 'normal'):
            body = str(msg['body'])
            if body.startswith('/'):
                cmd, arg_string = body.split(' ', maxsplit=1)
                cmd = cmd.lstrip('/')

                if arg_string:
                    args = arg_string.split(' ')
                else:
                    args = None

                self.log('IRC remote command received:', cmd, args)
                return
            else:
                if True:
                    msg.reply("Sorry, I did not understand that:\n%s" % body).send()

    def send_irc_message(self, event):
        """Transmit a message to a user"""

        self.log('Transmitting IRC message', lvl=debug)

        self.fireEvent(PRIVMSG(event.username, "[%s] %s : %s" % (event.msg_type, event.subject, event.body)))

    def stopped(self, event, source):
        """Stop the IRC connection"""

        self.log('Disconnecting IRC bot')
        self.fire(disconnect())

    def keepalive(self):
        """Keep server connection alive"""

        self.fire(write(b"\x00"))

    def error(self, *args):
        """Internal transport error, try to reconnect, if disconnected"""

        self.log("ERROR:", args)
        if not self.transport.connected:
            Timer(5, connect(self.host, self.port)).register(self)

    def connected(self, host, port):
        """Connected Event
        This event is triggered by the underlying ``TCPClient`` Component
        when a successfully connection has been made.
        """

        nick = self.nick
        hostname = self.hostname
        name = "{0:s} on {1:s} using isomer/{2:s}".format(
            nick, hostname, '1.0'
        )

        self.fire(USER(nick, hostname, host, name))
        self.fire(NICK(nick))

    def disconnected(self):
        """Disconnected Event
        This event is triggered by the underlying ``TCPClient`` Component
        when the active connection has been terminated.
        """

        self.fire(connect(self.host, self.port))

    def numeric(self, source, numeric, target, *args):
        """Numeric Event
        This event is triggered by the ``IRC`` Protocol Component when we have
        received an IRC Numeric Event from server we are connected to.
        """

        if numeric == ERR_NICKNAMEINUSE:
            self.fire(NICK("{0:s}_{1:d}".format(args[0], randint(0, 32768))))
        elif numeric in (RPL_ENDOFMOTD, ERR_NOMOTD):
            for irc_channel in self.irc_channels:
                self.fire(JOIN(irc_channel['name'], keys=irc_channel.get('key', None)))

    def join(self, source, channel):
        """Join Event
        This event is triggered by the ``IRC`` Protocol Component when a
        user has joined a channel.
        """

        self.channel_map[channel].add(source[0])
        self.nick_map[source[0]].add(channel)

        self.log("*** {0:s} has joined {1:s}".format(source[0], channel))

    def part(self, source, channel, reason=None):
        """Part Event
        This event is triggered by the ``IRC`` Protocol Component when a
        user has left a channel.
        """

        self.channel_map[channel].remove(source[0])
        self.nick_map[source[0]].remove(channel)

        self.log("*** {0:s} has left {1:s} ({2:s})".format(source[0], channel, reason or ""))

    def quit(self, source, message):
        """Quit Event
        This event is triggered by the ``IRC`` Protocol Component when a
        user has quit the network.
        """

        for irc_channel in self.nick_map[source[0]]:
            self.channel_map[irc_channel].remove(source[0])

        self.log("*** {0:s} has quit IRC".format(source[0]))

        del self.nick_map[source[0]]

    @handler("privmsg", "notice")
    def message(self, source, target, message):
        """Message Event
        This event is triggered by the ``IRC`` Protocol Component for each
        message we receieve from the server.
        """

        if target == self.nick or message.upper().startswith(self.nick.upper()):
            self.log('I was addressed! Source:', source, 'Message:', message)
            if "test_irc_send" in message:
                self.log('Testing via irc')
                self.fireEvent(cli_test_irc_send(), 'hfosweb')

        # Only log messages to the channel we're on
        if target[0] == "#":
            self.log(u"<{0:s}> {1:s}".format(source[0], message), "logger.{0:s}".format(target))

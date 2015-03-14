"""
Hackerfleet Operating System - Backend

Module: Chat
============

Chat manager

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

import json

from circuits.net.events import write
from circuits import Component, handler

from hfos.logger import hfoslog, error

from hfos.events import send


class Chat(Component):
    """
    Chat manager

    Handles
    * incoming chat messages
    * chat broadcasts
    """
    channel = "chat"

    def __init__(self, *args):
        super(Chat, self).__init__(*args)

        hfoslog("CHAT: Started")
        self._clients = []

    @handler("authentication")
    def authentication(self, event):
        try:
            hfoslog("Adding new user:", event.useruuid)
            if not event.useruuid in self._clients:
                self._clients.append(event.useruuid)
        except Exception as e:
            hfoslog("chat authentication event failed:", e, type(e), lvl=error)

    def _broadcast(self, chatpacket):
        hfoslog("CHAT: Transmitting message '%s'" % chatpacket)
        try:
            hfoslog("Recipients:", self._clients)
            for recipient in self._clients:
                self.fireEvent(send(recipient, chatpacket), "wsserver")
        except Exception as e:
            hfoslog("chat broadcast failed:", e, type(e), lvl=error)

    def _getusername(self, event):
        try:
            username = event.sender.profile.nick
        except AttributeError:
            username = event.sender.account.username
        return username

    @handler("chatevent")
    def on_chatevent(self, event):
        """Chat event handler for incoming events"""

        hfoslog("CHAT: Event: '%s'" % event.__dict__)
        try:
            data = event.content
            username = self._getusername(event)

            msg = ""

            if data['type'] == "msg":
                chatpacket = {'type': 'chat',
                              'content': {
                                  'sender': username,
                                  'timestamp': event.timestamp,
                                  'content': ":" + str(data['content'])
                              }
                }

            try:
                self._broadcast(chatpacket)
            except Exception as e:
                hfoslog("CHAT: Transmission error before broadcast: %s" % e, lvl=error)

                #if msgtype == "part" and event.sender in self._clients:
                #    self._clients.remove(event.sender)

        except Exception as e:
            hfoslog("CHAT: Error: '%s' %s" % (e, type(e)), lvl=error)

    @handler("chatmessage")
    def on_chatmessage(self, event):
        """Handles new incoming chat messages by broadcasting them to all connected clients"""
        hfoslog("CHAT: Event: '%s'" % event.__dict__)

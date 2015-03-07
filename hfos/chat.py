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

        print("CHAT: Started")
        self._clients = []

    def _broadcast(self, chatpacket):
        print("CHAT: Transmitting message '%s'" % chatpacket)
        for recipient in self._clients:
            self.fireEvent(write(recipient.sock, json.dumps(chatpacket)), "wsserver")

    def _getusername(self, event):
        try:
            username = event.sender.profile.nick
        except AttributeError:
            username = event.sender.account.username
        return username

    @handler("chatevent")
    def on_chatevent(self, event):
        """Chat event handler for incoming events"""

        print("CHAT: Event: '%s'" % event.__dict__)
        try:
            msgtype = event.msgtype
            username = self._getusername(event)

            msg = ""

            if msgtype == "join":
                self._clients.append(event.sender)
                msg = "joined"
            #if msgtype == "part":
            #    msg = "left"
            #    if event.sender in self._clients:
            #        self._clients.remove(event.sender)
            # TODO: Make this a representation of the event itself
            try:
                chatpacket = {'type': 'chat',
                              'content': {
                                  'sender': username,
                                  'timestamp': event.timestamp,
                                  'content': msg
                              }
                }
                self._broadcast(chatpacket)
            except Exception as e:
                print("CHAT: Transmission error before broadcast: %s" % e)

                #if msgtype == "part" and event.sender in self._clients:
                #    self._clients.remove(event.sender)

        except Exception as e:
            print("CHAT: Error: '%s' %s" % (e, type(e)))

    @handler("chatmessage")
    def on_chatmessage(self, event):
        """Handles new incoming chat messages by broadcasting them to all connected clients"""
        print("CHAT: Event: '%s'" % event.__dict__)
        try:
            # TODO: Make this a representation of the event itself
            chatpacket = {'type': 'chat',
                          'content': {
                              'sender': self._getusername(event),
                              'timestamp': event.timestamp,
                              'content': ":" + str(event.msg)
                          }
            }
            self._broadcast(chatpacket)
        except Exception as e:
            print("CHAT: Error: '%s'" % e)
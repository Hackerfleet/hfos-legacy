"""

Module: Chat
============

Chat manager

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from time import time
from __builtin__ import str as text
from circuits import Component

from hfos.logger import hfoslog, error, warn
from hfos.events import broadcast


class Chat(Component):
    """
    Chat manager

    Handles
    * incoming chat messages
    * chat broadcasts
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(Chat, self).__init__(*args)

        hfoslog("[CHAT] Started")

    def _getusername(self, event):
        try:
            try:
                username = event.user.profile.nick
            except AttributeError:
                hfoslog("[CHAT] Nickname not found.")
                username = event.user.account.username

            try:
                username += "@" + event.client.config.name
            except AttributeError:
                hfoslog("[CHAT] Client name not found.")

        except:
            hfoslog("[CHAT] Couldn't find user- or clientname: ",
                    event.user.profile.to_dict(),
                    event.client.config.to_dict(), lvl=warn)
            username = "Karl Ramseier"
        return username

    def chatrequest(self, event):
        """Chat event handler for incoming events
        :param event: ChatRequest with incoming chat message
        """

        hfoslog("[CHAT] Event: '%s'" % event.__dict__)
        try:
            action = event.action
            data = event.data
            username = self._getusername(event)

            if action == "say":
                chatpacket = {'component': 'chat',
                              'action': 'broadcast',
                              'data': {
                                  'sender': username,
                                  'timestamp': time(),
                                  'content': data.encode('utf-8')
                              }
                              }
            else:
                hfoslog("[CHAT] Unsupported action: ", action, event, lvl=warn)
                return

            try:
                self.fireEvent(broadcast("users", chatpacket))
            except Exception as e:
                hfoslog("[CHAT] Transmission error before broadcast: %s" % e, lvl=error)

        except Exception as e:
            hfoslog("[CHAT] Error: '%s' %s" % (e, type(e)), lvl=error)

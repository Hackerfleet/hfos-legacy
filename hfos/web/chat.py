"""

Module: Chat
============

Chat manager

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from time import time

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

        hfoslog("CHAT: Started")

    def _getusername(self, event):
        try:
            username = event.user.profile.nick
        except AttributeError:
            username = event.user.account.username
        return username

    def chatrequest(self, event):
        """Chat event handler for incoming events"""

        hfoslog("CHAT: Event: '%s'" % event.__dict__)
        try:
            action = event.action
            data = event.data
            username = self._getusername(event)

            msg = ""

            if action == "say":
                chatpacket = {'component': 'chat',
                              'action': 'broadcast',
                              'data': {
                                  'sender': username,
                                  'timestamp': time(),
                                  'content': ":" + str(data)
                              }
                              }
            else:
                hfoslog("CHAT: Unsupported action: ", action, event, lvl=warn)
                return

            try:
                self.fireEvent(broadcast("users", chatpacket))
            except Exception as e:
                hfoslog("CHAT: Transmission error before broadcast: %s" % e, lvl=error)

        except Exception as e:
            hfoslog("CHAT: Error: '%s' %s" % (e, type(e)), lvl=error)

"""

Module: Chat
============

Chat manager

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from time import time
from hfos.component import ConfigurableComponent
from hfos.logger import hfoslog, error, warn
from hfos.events import broadcast

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


class Chat(ConfigurableComponent):
    """
    Chat manager

    Handles
    * incoming chat messages
    * chat broadcasts
    """

    configprops = {}
    channel = "hfosweb"

    def __init__(self, *args):
        super(Chat, self).__init__("CHAT", *args)

        self.log("Started")

    def _getusername(self, event):
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

        except:
            self.log("Couldn't find user- or clientname: ",
                     event.user.profile.to_dict(),
                     event.client.config.to_dict(), lvl=warn)
            username = "NO USERNAME"
        return username

    def chatrequest(self, event):
        """Chat event handler for incoming events
        :param event: ChatRequest with incoming chat message
        """

        self.log("Event: '%s'" % event.__dict__)
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
                                  'content': str(data.encode('utf-8'))
                              }
                              }
            else:
                self.log("Unsupported action: ", action, event, lvl=warn)
                return

            try:
                self.fireEvent(broadcast("users", chatpacket))
            except Exception as e:
                self.log("Transmission error before broadcast: %s" % e,
                         lvl=error)

        except Exception as e:
            self.log("Error: '%s' %s" % (e, type(e)), lvl=error)

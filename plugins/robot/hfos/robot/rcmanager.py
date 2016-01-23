"""


Module: Chat
============

Chat manager

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from circuits import Component

from hfos.logger import hfoslog, error, warn, critical
from hfos.events import remotecontrolupdate, send


class RemoteControlManager(Component):
    """
    Remote Control manager

    Handles
    * incoming remote control messages
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(RemoteControlManager, self).__init__(*args)

        self.remotecontroller = None

        hfoslog("[RCM] Started")

    def clientdisconnect(self, event):
        """Handler to deal with a possibly disconnected remote controlling client
        :param event: ClientDisconnect Event
        """

        try:
            if event.clientuuid == self.remotecontroller:
                hfoslog("[RCM] Remote controller disconnected!", lvl=critical)
                self.remotecontroller = None
        except Exception as e:
            hfoslog("[RCM] Strange thing while client disconnected", e, type(e))

    def remotecontrolrequest(self, event):
        """Remote control event handler for incoming events
        :param event: RemoteControlRequest with action being one of
            ['takeControl', 'leaveControl', 'controlData']
        """

        hfoslog("[RCM] Event: '%s'" % event.__dict__)
        try:
            action = event.action
            data = event.data
            username = event.user.account.name
            clientname = event.client.name
            clientuuid = event.client.uuid

            if action == "takeControl":
                hfoslog("[RCM] Client wants to remote control: ", username, clientname, lvl=warn)
                if not self.remotecontroller:
                    hfoslog("[RCM] Success!")
                    self.remotecontroller = clientuuid
                    self.fireEvent(send(clientuuid, {'component': 'remotectrl', 'action': 'takeControl', 'data': True}))
                else:
                    hfoslog("[RCM] No, we're already being remote controlled!")
                    self.fireEvent(
                        send(clientuuid, {'component': 'remotectrl', 'action': 'takeControl', 'data': False}))
                return
            elif action == "leaveControl":
                if self.remotecontroller == event.client.uuid:
                    hfoslog("[RCM] Client leaves control!", username, clientname, lvl=warn)
                    self.remotecontroller = None
                    self.fireEvent(
                        send(clientuuid, {'component': 'remotectrl', 'action': 'takeControl', 'data': False}))
                return
            elif action == "controlData":
                hfoslog("[RCM] Control data received: ", data)
                if event.client.uuid == self.remotecontroller:
                    hfoslog("[RCM] Valid data, handing on to machineroom.")
                    self.fireEvent(remotecontrolupdate(data), "machineroom")
                else:
                    hfoslog("[RCM] Invalid control data update request!", lvl=warn)

        except Exception as e:
            hfoslog("[RCM] Error: '%s' %s" % (e, type(e)), lvl=error, exc=True)

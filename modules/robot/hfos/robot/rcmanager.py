"""


Module: Chat
============

Chat manager

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent
from hfos.logger import error, warn, critical
from hfos.events import remotecontrolupdate, send

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


class RemoteControlManager(ConfigurableComponent):
    """
    Remote Control manager

    Handles
    * incoming remote control messages
    """

    configprops = {}
    channel = "hfosweb"

    def __init__(self, *args):
        super(RemoteControlManager, self).__init__("RCM", *args)

        self.remotecontroller = None

        self.log("Started")

    def clientdisconnect(self, event):
        """Handler to deal with a possibly disconnected remote controlling
        client
        :param event: ClientDisconnect Event
        """

        try:
            if event.clientuuid == self.remotecontroller:
                self.log("Remote controller disconnected!", lvl=critical)
                self.remotecontroller = None
        except Exception as e:
            self.log("Strange thing while client disconnected", e, type(e))

    def remotecontrolrequest(self, event):
        """Remote control event handler for incoming events
        :param event: RemoteControlRequest with action being one of
            ['takeControl', 'leaveControl', 'controlData']
        """

        self.log("Event: '%s'" % event.__dict__)
        try:
            action = event.action
            data = event.data
            username = event.user.account.name
            clientname = event.client.name
            clientuuid = event.client.uuid

            if action == "takeControl":
                self.log("Client wants to remote control: ", username,
                         clientname, lvl=warn)
                if not self.remotecontroller:
                    self.log("Success!")
                    self.remotecontroller = clientuuid
                    self.fireEvent(send(clientuuid, {'component': 'remotectrl',
                                                     'action': 'takeControl',
                                                     'data': True}))
                else:
                    self.log("No, we're already being remote controlled!")
                    self.fireEvent(
                        send(clientuuid, {'component': 'remotectrl',
                                          'action': 'takeControl',
                                          'data': False}))
                return
            elif action == "leaveControl":
                if self.remotecontroller == event.client.uuid:
                    self.log("Client leaves control!", username, clientname,
                             lvl=warn)
                    self.remotecontroller = None
                    self.fireEvent(
                        send(clientuuid, {'component': 'remotectrl',
                                          'action': 'takeControl',
                                          'data': False}))
                return
            elif action == "controlData":
                self.log("Control data received: ", data)
                if event.client.uuid == self.remotecontroller:
                    self.log("Valid data, handing on to machineroom.")
                    self.fireEvent(remotecontrolupdate(data), "machineroom")
                else:
                    self.log("Invalid control data update request!", lvl=warn)

        except Exception as e:
            self.log("Error: '%s' %s" % (e, type(e)), lvl=error, exc=True)

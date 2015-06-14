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
from hfos.database import controllableobject, controllerobject


class DBAccessManager(Component):
    """Experimental: A component that is database aware and can retrieve certain things via warmongo"""

    def _getobjectlist(self, objecttype, conditions=None):
        """Gets objects off the database"""

        try:
            result = {}
            for item in objecttype.find(conditions):
                result[item.uuid] = item.serializablefields()
            return result
        except Exception as e:
            hfoslog("Error during list retrieval:", e, type(e), lvl=error)


class RemoteControlManager(DBAccessManager):
    """
    Remote Control manager

    Handles
    * incoming remote control messages
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(RemoteControlManager, self).__init__(*args)

        self.remotecontroller = None

        hfoslog("RMTCTRL: Started")

    def clientdisconnect(self, event):
        """Handler to deal with a possibly disconnected remote controlling client
        :param event: ClientDisconnect Event
        """

        try:
            if event.clientuuid == self.remotecontroller:
                hfoslog("RMTRCTRL: Remote controller disconnected!", lvl=critical)
                self.remotecontroller = None
        except Exception as e:
            hfoslog("RMTRCTRL: Strange thing while client disconnected", e, type(e))

    def remotecontrolrequest(self, event):
        """Remote control event handler for incoming events
        :param event: RemoteControlRequest with action being one of
            ['list', 'takeControl', 'leaveControl', 'controlData']
        """

        hfoslog("RMTCTRL: Event: '%s'" % event.__dict__)
        try:
            action = event.action
            data = event.data
            username = event.user.account.username
            clientname = event.client.name
            clientuuid = event.client.clientuuid

            if action == 'list':
                try:
                    dblist = {'controllables': self._getobjectlist(controllableobject),
                              'controllers': self._getobjectlist(controllerobject)}

                    self.fireEvent(send(clientuuid, {'component': 'remotectrl', 'action': 'list', 'data': dblist}))
                except Exception as e:
                    hfoslog("RCM: Listing error: ", e, type(e), lvl=error)
                return

            if action == "takeControl":
                hfoslog("Client wants to remote control: ", username, clientname, lvl=warn)
                if not self.remotecontroller:
                    hfoslog("Success!")
                    self.remotecontroller = clientuuid
                    self.fireEvent(send(clientuuid, {'component': 'remotectrl', 'action': 'takeControl', 'data': True}))
                else:
                    hfoslog("No, we're already being remote controlled!")
                    self.fireEvent(
                        send(clientuuid, {'component': 'remotectrl', 'action': 'takeControl', 'data': False}))
                return
            elif action == "leaveControl":

                if self.remotecontroller == event.client.clientuuid:
                    hfoslog("RMTCTRL: Client leaves control!", username, clientname, lvl=warn)
                    self.remotecontroller = None
                    self.fireEvent(
                        send(clientuuid, {'component': 'remotectrl', 'action': 'takeControl', 'data': False}))
                return
            elif action == "controlData":
                hfoslog("RMTCTRL: Control data received: ", data)
                if event.client.clientuuid == self.remotecontroller:
                    hfoslog("RMTCTRL: Valid data, handing on to ControlDataManager.")
                    self.fireEvent(remotecontrolupdate(data), "machineroom")
                else:
                    hfoslog("RMTCTRL: Invalid control data update request!", lvl=warn)

        except Exception as e:
            hfoslog("RMTCTRL: Error: '%s' %s" % (e, type(e)), lvl=error)

"""


Module: Chat
============

Chat manager

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.robot.events import control_update

from hfos.component import ConfigurableComponent, authorizedevent, handler
from hfos.events.client import send
from hfos.logger import warn, critical

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


# Remote Control events

class control_request(authorizedevent):
    """A client wants to remote control a servo"""


class control_release(authorizedevent):
    """A client wants to remote control a servo"""


class data(authorizedevent):
    """A client wants to remote control a servo"""


class RemoteControlManager(ConfigurableComponent):
    """
    Robotics remote control manager

    Handles
    * authority of controlling clients
    * incoming remote control messages
    """

    configprops = {}
    channel = "hfosweb"

    def __init__(self, *args):
        super(RemoteControlManager, self).__init__("RCM", *args)

        self.remote_controller = None

        self.log("Started")

    def clientdisconnect(self, event):
        """Handler to deal with a possibly disconnected remote controlling
        client
        :param event: ClientDisconnect Event
        """

        try:
            if event.clientuuid == self.remote_controller:
                self.log("Remote controller disconnected!", lvl=critical)
                self.remote_controller = None
        except Exception as e:
            self.log("Strange thing while client disconnected", e, type(e))

    @handler(control_request)
    def control_request(self, event):
        username = event.user.account.name
        client_name = event.client.name
        client_uuid = event.client.uuid

        self.log("Client wants to remote control: ", username,
                 client_name, lvl=warn)
        if not self.remote_controller:
            self.log("Success!")
            self.remote_controller = client_uuid
            self.fireEvent(send(client_uuid, {
                'component': 'hfos.robot.rcmanager',
                'action': 'control_request',
                'data': True
            }))
        else:
            self.log("No, we're already being remote controlled!")
            self.fireEvent(send(client_uuid, {
                'component': 'hfos.robot.rcmanager',
                'action': 'control_request',
                'data': False
            }))

        return

    @handler(control_release)
    def control_release(self, event):
        username = event.user.account.name
        client_name = event.client.name
        client_uuid = event.client.uuid

        if self.remote_controller == event.client.uuid:
            self.log("Client leaves control!", username, client_name,
                     lvl=warn)
            # TODO: Switch to a possible fallback controller
            self.remote_controller = None
            self.fireEvent(send(client_uuid, {
                'component': 'hfos.robot.rcmanager',
                'action': 'control_release',
                'data': True
            }))
        return

    @handler(data)
    def data(self, event):
        control_data = event.data

        self.log("Control data received: ", control_data)
        if event.client.uuid == self.remote_controller:
            self.log("Valid data, handing on to machineroom.")
            self.fireEvent(control_update(control_data), "machineroom")
        else:
            self.log("Invalid control data update request!", lvl=warn)

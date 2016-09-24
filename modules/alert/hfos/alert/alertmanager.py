"""

Module: AlertManager
====================

AlertManager

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from circuits import handler
from hfos.component import ConfigurableComponent
from hfos.logger import hfoslog, error, warn, verbose, critical
from hfos.events.client import broadcast, send

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


class AlertManager(ConfigurableComponent):
    """
    AlertManager manager

    Handles
    * incoming AlertManager messages
    * AlertManager broadcasts
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(AlertManager, self).__init__("ALERT", *args)

        self.log("Started")

        self.referenceframe = None
        self.mobalert = False
        self.alertlist = []

    @handler('referenceframe', channel='navdata')
    def referenceframe(self, event):
        """Handles navigational reference frame updates.
        These are necessary to assign geo coordinates to alerts and other
        misc things.

        :param event with incoming referenceframe message
        """

        self.log("Got a reference frame update! ", event, lvl=verbose)

        self.referenceframe = event.data

    def userlogin(self, event):
        """Checks if an alert is ongoing and alerts the newly connected
        client, if so."""

        clientuuid = event.clientuuid

        if self.mobalert:
            alertpacket = {'component': 'alert', 'action': 'mob', 'data': True}
            self.fireEvent(send(clientuuid, alertpacket))

    def _recordMobAlert(self):
        self.alertlist.append(self.referenceframe)

    def alertrequest(self, event):
        """AlertManager event handler for incoming events

        :param event with incoming AlertManager message
        """

        self.log("Event: '%s'" % event.__dict__)
        try:
            action = event.action
            data = event.data

            if action == 'mob':
                # noinspection PySimplifyBooleanCheck,PySimplifyBooleanCheck
                if data == True:
                    self.log("MOB ALERT ACTIVATED.", lvl=critical)

                    self.mobalert = True
                    self._recordMobAlert()

                    alertpacket = {'component': 'alert', 'action': 'mob',
                                   'data': True}
                else:
                    self.log("MOB deactivation requested by ",
                            event.user.account.name, lvl=warn)
                    self.mobalert = False

                    alertpacket = {'component': 'alert', 'action': 'mob',
                                   'data': False}
            else:
                self.log("Unsupported action requested: ", event,
                        lvl=warn)
                return

            try:
                self.fireEvent(broadcast("users", alertpacket))
            except Exception as e:
                self.log("Transmission error before broadcast: %s" % e,
                        lvl=error)

        except Exception as e:
            self.log("Error: '%s' %s" % (e, type(e)), lvl=error)

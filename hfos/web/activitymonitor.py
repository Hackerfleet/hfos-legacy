"""

Module: ActivityMonitor 
=======================

Surveillance piece to check out what the users are doing, so the system can react
accordingly (e.g. not disturb with unimportant alerts when user is actively doing something)

Possibilities:
* check if users noticed an alert
* notify users, about what other users are doing
* offer further information
* achievements ;) (stared 100 hours at the map)

Should be user configurable and toggleable, at least most parts/bits.

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from circuits import handler
from hfos.component import ConfigurableComponent

from hfos.logger import hfoslog, error, warn, verbose, critical
from hfos.events import broadcast, send


class ActivityMonitor(ConfigurableComponent):
    """
    ActivityMonitor manager

    Handles
    * incoming ActivityMonitor messages
    * ActivityMonitor broadcasts
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(ActivityMonitor, self).__init__('ACTIVITY', *args)

        self.log("Started")

        self.referenceframe = None
        self.mobalert = False
        self.alertlist = []

    @handler('referenceframe', channel='navdata')
    def referenceframe(self, event):
        """Handles navigational reference frame updates.
        These are necessary to assign geo coordinates to alerts and other misc things.

        :param event with incoming referenceframe message
        """

        self.log("Got a reference frame update! ", event, lvl=verbose)

        self.referenceframe = event.data

    def userlogin(self, event):
        """Checks if an alert is ongoing and alerts the newly connected client, if so."""

        clientuuid = event.clientuuid

        if self.mobalert:
            alertpacket = {'component': 'alert', 'action': 'mob', 'data': True}
            self.fireEvent(send(clientuuid, alertpacket))

    def _recordMobAlert(self):
        self.alertlist.append(self.referenceframe)

    def activityrequest(self, event):
        """ActivityMonitor event handler for incoming events

        :param event with incoming ActivityMonitor message
        """

        self.log("Event: '%s'" % event.__dict__)
        try:
            action = event.action
            data = event.data


        except Exception as e:
            self.log("Error: '%s' %s" % (e, type(e)), lvl=error)

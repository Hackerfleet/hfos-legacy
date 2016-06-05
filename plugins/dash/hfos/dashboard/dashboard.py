"""


Module: Dashboard
=================

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from hfos.component import ConfigurableComponent
from hfos.database import objectmodels
from hfos.logger import hfoslog, error, warn, critical
from datetime import datetime
from hfos.events import updatesubscriptions, send


class Dashboard(ConfigurableComponent):
    """
    The Dashboard component checks on the existing dashboard watering rules and
    triggers pump start/stop events accordingly. It also accepts interrupt
    notifications from authorized users to start/stop/suspend the watering
    plan.
    In future, it should also monitor weather and sensor data to water
    efficiently.
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the Dashboard component.

        :param args:
        """

        super(Dashboard, self).__init__("Dashboard", *args)

        self.log("Started")

    def dashboardrequest(self, event):
        self.log("Someone interacts with the dashboard! Yay!", lvl=warn)

    def objectcreation(self, event):
        self.log("Foo, bar: ", event)

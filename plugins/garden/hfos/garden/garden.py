"""


Module: Garden
==============

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from hfos.component import ConfigurableComponent
from hfos.database import objectmodels
from hfos.logger import hfoslog, error, warn, critical
from datetime import datetime
from hfos.events import updatesubscriptions, send


class Garden(ConfigurableComponent):
    """
    The Garden component checks on the existing garden watering rules and
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
        Initialize the Garden component.

        :param args:
        """

        super(Garden, self).__init__("GARDEN", *args)

        self.log("Started")

    def gardenrequest(self, event):
        self.log("Someone interacts with the garden! Yay!", lvl=warn)

    def objectcreation(self, event):
        if event.schema == 'wateringrule':
            self.log("Reloading rules")
        self._reloadWateringRules()

    def _reloadWateringRule(self):
        """
        Reloads all stored watering rules.
        """
        self.log("No, not yet.")

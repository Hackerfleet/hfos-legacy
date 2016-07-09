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
    The Dashboard component monitors dashboard changes. It does not do much.
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the Dashboard component.

        :param args:
        """

        super(Dashboard, self).__init__("DASH", *args)

        self.log("Started")

    def dashboardrequest(self, event):
        self.log("Someone interacts with the dashboard! Yay!", lvl=warn)

    def objectcreation(self, event):
        if event.schema == 'dashboardconfig':
            self.log("Dashboarconfig was modified: ", event)


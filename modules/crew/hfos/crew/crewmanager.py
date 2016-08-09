"""


Module: Crewmanager
===================

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent
from hfos.logger import warn  # , hfoslog, error, critical

# from hfos.database import objectmodels
# from datetime import datetime
# from hfos.events.system import updatesubscriptions, send

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


class Crewmanager(ConfigurableComponent):
    """
    The Crew component monitors crew changes. It does not do much.
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the Crew component.

        :param args:
        """

        super(Crewmanager, self).__init__("CREW", *args)

        self.log("Started")

    def crewrequest(self, event):
        self.log("Someone interacts with the crew! Yay!", event, lvl=warn)

    def objectcreation(self, event):
        if event.schema == 'crewconfig':
            self.log("Crewconfig was modified: ", event)

"""


Module: LogbookWatcher
======================

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent
from hfos.logger import warn  # , hfoslog, error, critical

# from hfos.database import objectmodels
# from datetime import datetime
# from hfos.events.system import updatesubscriptions, send

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


class Logbookwatcher(ConfigurableComponent):
    """
    The LogbookWatcher component monitors logbook changes. It does not do much.
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the LogbookWatcher component.

        :param args:
        """

        super(Logbookwatcher, self).__init__("LOGBOOK", *args)

        self.log("Started")

    def logbookrequest(self, event):
        self.log("Someone interacts with the logbook! Yay!", event, lvl=warn)

    def objectcreation(self, event):
        if event.schema in ('logbookentry', 'logbookconfig'):
            self.log("Logbook related item was modified: ", event)

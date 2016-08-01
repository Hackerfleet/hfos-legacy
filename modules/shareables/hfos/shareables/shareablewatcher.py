"""


Module: Shareables
==================

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent
from hfos.database import objectmodels
from hfos.logger import hfoslog, error, warn, critical, events
from hfos.events import AuthorizedEvent, AuthorizedEvents
from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


class ShareableWatcher(ConfigurableComponent):
    """
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the ShareableWatcher component.

        :param args:
        """

        super(ShareableWatcher, self).__init__("SHAREABLE", *args)

        self.log("Started")

    def objectcreation(self, event):
        if event.schema == 'shareable':
            self.log("Updating shareables")

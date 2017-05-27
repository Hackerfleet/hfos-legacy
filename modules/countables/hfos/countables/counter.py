"""


Module: Countables
==================

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent, handler
from hfos.database import objectmodels
from hfos.logger import hfoslog, error, warn, critical, events
from hfos.events.system import authorizedevent
from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


class increment(authorizedevent):
    """Increments the counter of a countable object"""


class Counter(ConfigurableComponent):
    """
    Watches for incrementation requests.
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the CountableWatcher component.

        :param args:
        """

        super(Counter, self).__init__("COUNT", *args)

        self.log("Started")

    @handler(increment)
    def increment(self, event):
        self.log(event.user.account.name, "counted another object!",
                 event.data)
        countable = objectmodels['countable'].find_one({'uuid': event.data})
        try:
            countable.amount += 1
        except AttributeError:
            # Was not initialized yet
            countable.amount = 1
        countable.save()

    def objectcreation(self, event):
        if event.schema == 'countable':
            self.log("Updating countables")

"""


Module: Countables
==================

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent
from hfos.database import objectmodels
from hfos.logger import hfoslog, error, warn, critical, events
from hfos.events import AuthorizedEvent, AuthorizedEvents

from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


class countrequest(AuthorizedEvent):
    def __init__(self, *args):
        super(countrequest, self).__init__(*args)
        hfoslog('Counterrequest generated:', args, emitter='COUNTER',
                lvl=events)

AuthorizedEvents['countablewatcher'] = countrequest


class CountableWatcher(ConfigurableComponent):
    """
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the CountableWatcher component.

        :param args:
        """

        super(CountableWatcher, self).__init__("COUNT", *args)

        self.log("Started")

    def countrequest(self, event):
        self.log(event.user.account.name, "counted another object!",
                 event.data)
        countable = objectmodels['countable'].find_one({'uuid': event.data})
        try:
            countable.amount += 1
        except (TypeError, AttributeError):
            # Was not initialized yet
            countable.amount = 1
        countable.save()

    def objectcreation(self, event):
        if event.schema == 'countable':
            self.log("Updating countables")

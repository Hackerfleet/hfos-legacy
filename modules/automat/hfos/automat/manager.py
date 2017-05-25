"""


Module: AutomatWatcher
======================

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent, authorizedevent, handler
from hfos.events.client import send
from circuits import Event
from hfos.logger import warn, error, critical, hilight
from copy import deepcopy

# from hfos.database import objectmodels
# from datetime import datetime
# from hfos.events.system import updatesubscriptions, send


__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


class store_rule(authorizedevent):
    """User requests to store a rule"""


class get_events(authorizedevent):
    """Requests a list of automatable events"""

    def __init__(self, *args, **kwargs):
        super(get_events, self).__init__(*args, **kwargs)
        print('AUTOMAT EVENT GENERATED')


class rule_triggered(Event):
    """An established rule has been triggered"""

    def __init__(self, *args):
        """
        """
        super(rule_triggered, self).__init__(*args)


class Manager(ConfigurableComponent):
    """
    The Automat Manager component monitors automat rule changes. It does not
    do much.
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the Automat Manager component.

        :param args:
        """

        super(Manager, self).__init__("AUTOMAT", *args)

        self.authorized_events = None

        self.log("Started")

    @handler(store_rule)
    def store_rule(self, event):
        print("TESTER CALLED!")

    @handler(get_events)
    def get_events(self, event):
        self.log('Automatable event list requested:', event.user.account.name)

        events = deepcopy(self.authorized_events)

        for source in events:
            for value in events[source].values():
                del(value['event'])

        from pprint import pprint
        pprint(events)

        packet = {
            'component': 'hfos.automat.manager',
            'action': 'get_events',
            'data': events
        }
        self.fireEvent(send(event.client.uuid, packet))

    def ready(self, event):
        from hfos.events.system import AuthorizedEvents
        self.authorized_events = AuthorizedEvents
        self.log('Automat Started, event sources:', AuthorizedEvents.keys())

    def objectcreation(self, event):
        if event.schema in ('automatentry', 'automatconfig'):
            self.log("Automat related item was modified: ", event)

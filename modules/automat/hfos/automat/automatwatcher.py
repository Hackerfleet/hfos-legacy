"""


Module: AutomatWatcher
======================

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent
from circuits import Event
from hfos.logger import warn  # , hfoslog, error, critical

# from hfos.database import objectmodels
# from datetime import datetime
# from hfos.events.system import updatesubscriptions, send

from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


class Automatwatcher(ConfigurableComponent):
    """
    The AutomatWatcher component monitors automat changes. It does not do much.
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the AutomatWatcher component.

        :param args:
        """

        super(Automatwatcher, self).__init__("AUTOMAT", *args)

        self.log("Started")

        eventclasses = self.inheritors(Event)
        self.log('Inherited classes:')
        pprint(eventclasses)

    def inheritors(self, klass):
        subclasses = set()
        work = [klass]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    pprint(child.__dict__)
                    name = child.__module__ + "." + child.__name__
                    if name.startswith('hfos'):

                        if not (name.startswith('hfos.events.client') or
                                    name.startswith('hfos.events.system')):
                            subclasses.add(name)
                    work.append(child)
        return subclasses

    def automatrequest(self, event):
        self.log("Someone interacts with the automat! Yay!", event, lvl=warn)

    def objectcreation(self, event):
        if event.schema in ('automatentry', 'automatconfig'):
            self.log("Automat related item was modified: ", event)

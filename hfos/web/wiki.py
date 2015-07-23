"""

Module: Wiki
============

Wiki manager

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from time import time
from __builtin__ import str as text
from circuits import Component

from hfos.logger import hfoslog, error, warn
from hfos.events import send
from hfos.database import wikipageobject


class Wiki(Component):
    """
    Wiki manager

    Handles
    * incoming page requests and updates
    * a list of registered pagenames
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(Wiki, self).__init__(*args)

        hfoslog("[WIKI] Started")

    def wikirequest(self, event):
        """Wiki event handler for incoming events
        :param event: WikiRequest with incoming wiki pagename and pagedata
        """

        hfoslog("[WIKI] Event: '%s'" % event.__dict__)
        try:
            action = event.action
            data = event.data

            if action == "get":
                wikipage = wikipageobject.find_one({'name': data})

                wikipacket = {'component': 'wiki',
                              'action': 'get',
                              'data': wikipage.serializablefields()
                              }
            else:
                hfoslog("[WIKI] Unsupported action: ", action, event, lvl=warn)
                return

            try:
                self.fireEvent(send(event.client.clientuuid, wikipacket))
            except Exception as e:
                hfoslog("[WIKI] Transmission error before broadcast: %s" % e, lvl=error)

        except Exception as e:
            hfoslog("[WIKI] Error: '%s' %s" % (e, type(e)), lvl=error)

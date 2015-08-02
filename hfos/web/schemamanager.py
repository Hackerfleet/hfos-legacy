"""

Module: SchemaManager
=====================

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from circuits import Component

import hfos.schemata
from hfos.logger import hfoslog, info
from hfos.events import send


class SchemaManager(Component):
    """
    Handles schemata requests from clients.
    """

    channel = "hfosweb"

    def schemarequest(self, event):
        """Handles schema requests.

        :param event: SchemaRequest with actions
        * Get
        * All
        """
        if event.action == "Get":
            hfoslog("[SM] Schemarequest for ", event.data, "from", event.user, lvl=info)
            if event.data in hfos.schemata.schemastore:
                response = {'component': 'schema',
                            'action': 'Get',
                            'data': self.schemata[event.data]
                            }
                self.fireEvent(send(event.client.uuid, response))
        elif event.action == "All":
            hfoslog("[SM] Schemarequest for all schemata from ", event.user, lvl=info)
            response = {'component': 'schema',
                        'action': 'All',
                        'data': hfos.schemata.schemastore}
            self.fireEvent(send(event.client.uuid, response))

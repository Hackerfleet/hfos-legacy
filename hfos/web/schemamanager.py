"""

Module: SchemaManager
=====================

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent
from hfos.database import schemastore
from hfos.logger import hfoslog, error
from hfos.events import send

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


class SchemaManager(ConfigurableComponent):
    """
    Handles schemata requests from clients.
    """

    channel = "hfosweb"

    configprops = {}

    def __init__(self, *args):
        super(SchemaManager, self).__init__('SM', *args)

    def schemarequest(self, event):
        """Handles schema requests.

        :param event: SchemaRequest with actions
        * Get
        * All
        """

        try:

            if event.action == "Get":
                self.log("Schemarequest for ", event.data, "from", event.user)
                if event.data in schemastore:
                    response = {'component': 'schema',
                                'action': 'Get',
                                'data': self.schemata[event.data]
                                }
                    self.fireEvent(send(event.client.uuid, response))
            elif event.action == "All":
                self.log("Schemarequest for all schemata from ", event.user)
                response = {'component': 'schema',
                            'action': 'All',
                            'data': schemastore}
                self.fireEvent(send(event.client.uuid, response))

        except Exception as e:
            self.log("Overall error: ", e, type(e), lvl=error, exc=True)

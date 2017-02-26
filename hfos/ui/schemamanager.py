"""

Module: SchemaManager
=====================

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.events.client import send
from hfos.component import ConfigurableComponent
from hfos.database import schemastore
from hfos.logger import error, warn

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


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
                                'data': schemastore[event.data]
                                }
                    self.fireEvent(send(event.client.uuid, response))
                else:
                    self.log("Unavailable schema requested!", lvl=warn)
            elif event.action == "All":
                self.log("Schemarequest for all schemata from ", event.user)
                response = {'component': 'schema',
                            'action': 'All',
                            'data': schemastore}
                self.fireEvent(send(event.client.uuid, response))

        except Exception as e:
            self.log("Overall error: ", e, type(e), lvl=error, exc=True)

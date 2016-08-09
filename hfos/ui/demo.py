"""

Module: Web.Demo
================

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

import json
from random import randint

from hfos.events.client import broadcast
from hfos.component import ConfigurableComponent

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


class WebDemo(ConfigurableComponent):
    """
    Demonstrates functionality by interactively playing back demo data.
    """

    channel = "hfosweb"

    def ping(self, *args):
        """Pings all connected clients with stupid ping/demo messages (for now)
        :param args:
        """

        self._count += 1
        self.log("Ping %i:" % self._count, args)

        data = {'component': 'ping',
                'action': "Hello"
                }
        if (self._count % 2) == 0:
            data = {'component': 'navdata',
                    'action': 'update',
                    'data': {'true_course': randint(0, 359),
                             'spd_over_grnd': randint(0, 50)
                             }
                    }
        self.fireEvent(broadcast("clients", json.dumps(data)))

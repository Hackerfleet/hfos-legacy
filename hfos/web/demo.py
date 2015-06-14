"""

Module: Web.Demo
================

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from random import randint
import json

from circuits import Component

from hfos.logger import hfoslog
from hfos.events import broadcast


class WebDemo(Component):
    """
    Demonstrates functionality by interactively playing back demo data.
    """

    channel = "hfosweb"

    def ping(self, *args):
        """Pings all connected clients with stupid ping/demo messages (for now)"""

        self._count += 1
        hfoslog("[DEMO] Ping %i:" % self._count, args)

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

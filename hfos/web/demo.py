"""
Hackerfleet Operating System - Backend

Module: Web.Demo
================

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = 'riot'

from random import randint
import json

from circuits import Component

from hfos.logger import hfoslog
from hfos.events import broadcast


class WebDemo(Component):
    """
    Handles schemata requests from clients.
    """

    channel = "hfosweb"

    def ping(self, *args, **kwargs):
        """Pings all connected clients with stupid ping/demo messages"""
        self._count += 1
        hfoslog("CA: Ping %i" % self._count)

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

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2017 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "GPLv3"

"""


Module: Shareables
==================


"""

from hfos.component import ConfigurableComponent, handler
from hfos.database import objectmodels
from hfos.logger import debug, error
from hfos.events.system import authorizedevent
from hfos.events.client import send

# from pprint import pprint


class reserve(authorizedevent):
    """Reserves a shareable object"""


class Manager(ConfigurableComponent):
    """
    Manages shareable resources.
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the ShareableWatcher component.

        :param args:
        """

        super(Manager, self).__init__("SHAREABLE", *args)

        self.log("Started")

    def objectcreation(self, event):
        if event.schema == 'shareable':
            self.log("Updating shareables")

    @handler(reserve)
    def reserve(self, event):
        try:
            uuid = event.data['uuid']
            reserve_from = event.data['from']
            reserve_to = event.data['to']
            reserve_title = None if 'title' not in event.data else \
                event.data['title']
            reserve_description = "" if 'description' not in event.data \
                else event.data['description']

            shareable_model = objectmodels['shareable']
            shareable = shareable_model.find_one({'uuid': uuid})

            early = shareable_model.find_one({
                'uuid': uuid,
                'reservations': {
                    '$elemMatch': {
                        'starttime': {'$lte': reserve_from},
                        'endtime': {'$gte': reserve_from}
                    }
                }
            })

            self.log('Any early reservation:', early, lvl=debug)

            late = shareable_model.find_one({
                'uuid': uuid,
                'reservations': {
                    '$elemMatch': {
                        'starttime': {'$lte': reserve_to},
                        'endtime': {'$gte': reserve_to}
                    }
                }
            })

            self.log('Any late reservation:', late, lvl=debug)

            if not late and not early:
                reservation = {
                    'useruuid': event.user.uuid,
                    'starttime': reserve_from,
                    'endtime': reserve_to,
                    'title': reserve_title if reserve_title else
                    "Reserved by " + event.user.account.name,
                    'description': reserve_description
                }
                shareable.reservations.append(reservation)
                shareable.save()
                self.log('Successfully stored reservation!')
                response = {
                    'component': 'hfos.shareables.manager',
                    'action': 'reserve',
                    'data': True
                }
            else:
                self.log('Not able to store reservation due to '
                         'overlapping reservations.')
                response = {
                    'component': 'hfos.shareables.manager',
                    'action': 'reserve',
                    'data': False
                }
            self.fireEvent(send(event.client.uuid, response))
        except Exception as e:
            self.log('Unknown failure:', e, type(e), exc=True)

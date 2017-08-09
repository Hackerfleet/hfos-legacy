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
Schema: Chat Lastlog
====================

Contains
--------

ChatLastlog: Lastlog to store lastlogs for users


"""

from hfos.schemata.defaultform import noform
from hfos.schemata.base import base_object

ChatLastlogSchema = base_object('chatlastlog', has_owner=True,
                                all_roles='owner')

ChatLastlogSchema['properties'].update({
     'channels': {
         'type': 'object',
     }
    #     'items': {
    #         'type': 'object',
    #         'properties': {
    #             'timestamp': {
    #                 'type': 'string', 'title': 'Timestamp',
    #                 'format': 'datetimepicker',
    #                 'description': 'Lastlog timestamp'
    #             },
    #             'channel': {
    #                 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{'
    #                            '4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
    #                 'type': 'string',
    #                 'title': 'Unique ID of channel'
    #             },
    #         }
    #     }
    # }
})

ChatLastlog = {'schema': ChatLastlogSchema, 'form': noform}

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
Schema: Chat Channel
====================

Contains
--------

ChatChannel: Definitions of chat rooms


"""

from hfos.schemata.defaultform import editbuttons
from hfos.schemata.base import base_object

ChannelSchema = base_object('chatchannel', all_roles='crew')

ChannelSchema['properties'].update({
    'users': {
        'type': 'array',
        'default': [],
        'items': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{'
                       '4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique User ID of participant'
        }
    },
    'topic': {
        'type': 'string'
    },
    'tags': {
        'type': 'string', 'title': 'Tags',
        'description': 'Attached tags'
    }
})

ChannelForm = [
    'name',
    'topic',
    'tags',
    editbuttons
]

ChatChannel = {'schema': ChannelSchema, 'form': ChannelForm}

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2018 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""
Schema: Chat Message
====================

Contains
--------

ChatMessage: ChatMessage to store messages in rooms and private chats


"""

from hfos.schemata.defaultform import defaultform
from hfos.schemata.base import base_object, uuid_object

ChatMessageSchema = base_object('chatmessage', all_roles='crew')

ChatMessageSchema['properties'].update({
    'timestamp': {'type': 'number', 'title': 'Timestamp',
                  'format': 'datetimepicker',
                  'description': 'Message timestamp'},
    'recipient': uuid_object('Unique User ID of recipient'),
    'sender': uuid_object('Unique User ID of sender'),
    'content': {'type': 'string', 'minLength': 1, 'title': 'Name',
                'description': 'Chat Message name'}
})

ChatMessage = {'schema': ChatMessageSchema, 'form': defaultform}

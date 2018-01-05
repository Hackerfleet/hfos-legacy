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
Schema: Log Message
==============

Contains
--------

LogMessage: LogMessage to store messages in rooms and private logs


"""

from hfos.schemata.defaultform import readonlyform
from hfos.schemata.base import base_object

LogMessageSchema = base_object('logmessage', no_perms=True)

LogMessageSchema.update({'roles_create': 'SYSTEM'})

LogMessageSchema['properties'].update({
    'timestamp': {'type': 'number', 'title': 'Timestamp',
                  'description': 'Log Message timestamp (\xc2Sec)'},
    'emitter': {'type': 'string', 'minLength': 1, 'title': 'Emitter',
                'description': 'Log Message emitter name'},
    'sourceloc': {'type': 'string', 'minLength': 1, 'title': 'Source '
                                                             'location',
                  'description': 'Log Message source code location'},
    'level': {'type': 'string', 'minLength': 1, 'title': 'Level',
              'description': 'Log Message elevation level'},
    'content': {'type': 'string', 'minLength': 1, 'title': 'Content',
                'description': 'Log Message content'}
})

LogOptions = {
    'disabled': True
}

LogMessage = {
    'schema': LogMessageSchema,
    'form': readonlyform,
    'options': LogOptions
}

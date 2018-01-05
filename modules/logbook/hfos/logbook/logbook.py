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

Schema: Logbook
===============

Contains
--------

Multiple logbook-entry and a general logbook schemata.

See also
--------

Provisions


"""

Incident = {

}

LogbookSchema = {
    'type': 'object',
    'id': '#logbook',
    'name': 'logbook',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36,
                 'title': 'Unique Logbook Event ID', 'description': 'HIDDEN'},
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
                 'description': 'Name of logbook entry'},
        'severity': {'type': 'string', 'enum': ['Info', 'Warning', 'Critical'],
                     'default': 'Info'},
        'owner': {'type': 'string', 'minLength': 36,
                  'title': "Owner's Unique ID", 'description': 'HIDDEN'},
        'time': {'type': 'string', 'format': 'datetimepicker',
                 'title': 'Event time',
                 'description': 'Date and time of event'},
        'category': {'type': 'string', 'title': 'Category',
                     'enum': ['Incident', 'Navigation', 'Technical', 'Bridge'],
                     'description': 'Category of log event'},
        'subcategory'
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                  'description': 'Entry notes'},

    }
}

Logbook = {'schema': LogbookSchema, 'form': {}}

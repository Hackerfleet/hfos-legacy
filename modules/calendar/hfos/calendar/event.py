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

Schema: Event
=============

Contains
--------

Event object for common item time sharing management

See also
--------

Provisions


"""

from hfos.schemata.base import uuid_object, base_object
from hfos.schemata.defaultform import editbuttons, section, fieldset, lookup_field  # , collapsible
from hfos.schemata.geometry import GeometrySchema

EventSchema = base_object('event', all_roles='crew')

EventSchema['properties'].update({
    "calendar": uuid_object('Associated calendar', display=True),
    "dtstart": {
        "format": "datetimepicker",
        "type": "string",
        "description": "Event starting time"
    },
    "dtend": {
        "format": "datetimepicker",
        "type": "string",
        "description": "Event ending time"
    },
    "summary": {"type": "string", "format": "html"},
    "location": {"type": "string"},
    "created": {"type": "string"},
    "timestamp": {"type": "string"},
    "modified": {"type": "string"},
    "status": {"type": "string"},
    "uid": {"type": "string"},
    "class": {"type": "string"},
    "url": {"type": "string", "format": "uri"},
    "color": {'type': 'string', 'format': 'color'},
    "duration": {
        "format": "timepicker",
        "type": "string",
        "description": "Event duration"
    },
    "recurring": {
        "type": "boolean",
        "title": "Recurring event",
        "default": False
    },
    "rdate": {
        "format": "datetimepicker",
        "type": "string",
        "description": "Recurrence date"
    },
    "rrule": {
        "type": "string",
        "description": "Recurrence rule"
    },
    "category": {"type": "string", "description": "Event category"},
    #"geo": GeometrySchema
})

EventForm = [
    fieldset('General', [
        section(3,2, [
            ['name', 'category'],
            ['dtstart', 'dtend'],
            ['duration', 'location']
        ]),
        section(1, 2, [[lookup_field('calendar'), 'color']]),
        'summary',
        'geo',
        'recurring'
    ]),
    fieldset('Recurrence', [
        section(1,2, [
            ['rdate', 'rrule']
        ])
    ], options={
        'condition': '$ctrl.model.recurring'
    }),
    editbuttons
]

Event = {'schema': EventSchema, 'form': EventForm}

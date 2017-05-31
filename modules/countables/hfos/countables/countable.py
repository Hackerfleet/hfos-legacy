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

Schema: Countable
=================

Contains
--------

Generic countable thing definition


"""

from hfos.schemata.defaultform import editbuttons
from hfos.schemata.base import base_object

CountableSchema = base_object('countable', all_roles='crew')

CountableSchema['properties'].update({
    'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
              'description': 'Entry notes'},
    'amount': {'type': 'number', 'title': 'Amount counted', 'default': 0}

})

CountableForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'name', 'notes'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'amount'

                ]
            },
        ]
    },
    {
        'key': 'count',
        'type': 'button',
        'onClick': '$ctrl.formAction("hfos.countables.counter", "increment", '
                   '$ctrl.model.uuid)',
        'title': '+1'
    },
    editbuttons
]

Countable = {'schema': CountableSchema, 'form': CountableForm}

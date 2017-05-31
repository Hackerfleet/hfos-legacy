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

Schema: Shareable
=================

Contains
--------

Shareable object for common item time sharing management

See also
--------

Provisions


"""

from hfos.schemata.base import base_object
from hfos.schemata.defaultform import editbuttons

ShareableSchema = base_object('shareable', all_roles='crew')

ShareableSchema['properties'].update({
    'creatoruuid': {'type': 'string', 'title': 'Creator',
                    'description': 'Creator of Shareable'},
    'created': {'type': 'string', 'format': 'datetimepicker',
                'title': 'Creation time',
                'description': 'Time of object creation'},
    'priority': {'type': 'number', 'title': 'Priority',
                 'description': '1 is Highest priority', 'minimum': 1},
    'tags': {'type': 'string', 'title': 'Tags',
             'description': 'Attached tags'},
    'notes': {'type': 'string', 'format': 'html', 'default': '',
              'title': 'Scheduled item notes',
              'description': 'Free text entry'},
    'reservations': {
        'type': 'array',
        'default': [],
        'items': {
            'type': 'object',
            'properties': {
                'useruuid': {'type': 'string', 'minLength': 36,
                             'title': 'User',
                             'description': 'Reserving User'},
                'starttime': {'type': 'string', 'format': 'datetimepicker',
                              'title': 'Begin',
                              'description': 'Begin of reservation'},
                'endtime': {'type': 'string', 'format': 'datetimepicker',
                            'title': 'End',
                            'description': 'End of reservation'},
                'title': {'type': 'string', 'title': 'Title',
                          'description': 'Reservation Title'},
                'description': {'type': 'string', 'title': 'Description',
                                'description': 'Reservation Details'}
            }
        }
    }
})

ShareableForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'name', {
                        'key': 'owner',
                        'type': 'strapselect',
                        'placeholder': 'Select an Owner',
                        'options': {
                            "type": "user",
                            "asyncCallback": "$ctrl.getFormData",
                            "map": {'valueProperty': "uuid",
                                    'nameProperty': 'name'}
                        },
                        "onChange": 'fieldChange(modelValue, form)'
                        #                             '''function (
                        # modelValue, form) {
                        # $scope.form.forEach(function (item) {
                        # if (item.key == "multiselectDynamicHttpGet") {
                        #     item.options.scope.populateTitleMap(item);
                        # }
                        # });
                        # alert("onChange happened!\nYou changed this value
                        # into " + modelValue + " !\nThen code in this event
                        #  cause the multiselectDynamicHttpGet to reload.
                        # \nSee the ASF onChange event for info.");
                        #
                        # '''
                    }, 'priority'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'tags', 'creatoruuid'
                ]
            },
        ]
    },
    {
        'key': 'created',
        'options': {
            "minuteStep": 15,
            "autoclose": 1
        }
    },
    'notes',
    # {
    #     'key': 'reservations',
    #     'add': "Add reservation",
    #     'startEmpty': False,
    #     'style': {
    #         'add': "btn-success"
    #     },
    #     'items': [
    #         'reservations[].title',
    #         {
    #             'key': 'reservations[].useruuid',
    #             'type': 'strapselect',
    #             'placeholder': 'Select an Owner',
    #             'options': {
    #                 "type": "user",
    #                 "asyncCallback": "$ctrl.getFormData",
    #                 "map": {'valueProperty': "uuid",
    #                         'nameProperty': 'name'}
    #             },
    #             "onChange": 'fieldChange(modelValue, form)'
    #         },
    #         {
    #             'htmlClass': 'col-md-2',
    #             'key': 'reservations[].starttime',
    #             'options': {
    #                 "minuteStep": 15,
    #                 "autoclose": 1
    #             }
    #         },
    #         {
    #             'htmlClass': 'col-md-2',
    #             'key': 'reservations[].endtime',
    #             'options': {
    #                 "minuteStep": 15,
    #                 "autoclose": 1
    #             },
    #         },
    #         'reservations[].description',
    #     ]
    # },
    editbuttons
]

Shareable = {'schema': ShareableSchema, 'form': ShareableForm}

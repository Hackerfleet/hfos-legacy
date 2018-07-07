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

Schema: Project
============

Contains
--------

Project reference entry for the todo management

See also
--------

Provisions


"""

from hfos.schemata.defaultform import editbuttons
from hfos.schemata.base import base_object

ProjectSchema = base_object('project', all_roles='crew')

ProjectSchema['properties'].update({
    'creatoruuid': {'type': 'string', 'title': 'Creator',
                    'description': 'Creator of Project'},
    'priority': {'type': 'number', 'title': 'Priority',
                 'description': '1 is Highest priority', 'minimum': 1},
    'tags': {'type': 'string', 'title': 'Tags',
             'description': 'Attached tags'},
    'notes': {'type': 'string', 'title': 'User notes',
              'description': 'Entry notes'}
})

ProjectForm = [
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
                    }, 'priority',
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
    'notes',
    editbuttons
]

Project = {
    'schema': ProjectSchema,
    'form': ProjectForm,
    'indices': {
        'name': {}
    }
}

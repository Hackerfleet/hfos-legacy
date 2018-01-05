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
Schema: WikiPage
================

Contains
--------

WikiPage: WikiPage to store collaborative data


"""

from hfos.schemata.defaultform import defaultform, editbuttons
from copy import deepcopy
from hfos.schemata.base import base_object

WikiPageSchema = base_object('wikipage', all_roles='crew')

WikiPageSchema['properties'].update({
    'title': {'type': 'string', 'title': 'Page Title',
              'description': 'Short title'},
    'html': {'type': 'string', 'format': 'html', 'title': 'Page content',
             'description': 'Content'},
    # 'text': {'type': 'string', 'title': 'Raw text',
    #          'description': 'Unrendered raw text'},
    # 'history': {
    #     'type': 'array',
    #     'default': [],
    #     'items': {
    #         'type': 'string',
    #         'title': 'Snapshot content',
    #         'description': 'Snapshot data'
    #     }
    # }
})

WikiPageForm = [
    'name',
    'title',
    'html',
    # {
    #     'key': 'html',
    #     'tinymceOptions': {
    #         'toolbar': [
    #             'undo redo | styleselect | bold italic | link image',
    #             'alignleft aligncenter alignright'
    #         ]
    #     }
    #
    {
        'type': 'button',
        'title': 'Go to Wiki',
        'onClick': "$ctrl.switchState('app.wiki', {name: $ctrl.model.name})",
        'condition': "$ctrl.action == 'Edit'"
    },
    editbuttons
]

WikiTemplateSchema = deepcopy(WikiPageSchema)
WikiTemplateSchema['id'] = '#wikitemplate'
WikiTemplateSchema['name'] = 'wikitemplate'
WikiTemplateSchema['properties']['slugtemplate'] = {
    'type': 'string',
    'title': 'Slug Template',
    'description': 'Template page name (url slug)'
}

WikiTemplateForm = deepcopy(WikiPageForm)
WikiTemplateForm.insert(1, 'slugtemplate')

WikiPage = {'schema': WikiPageSchema, 'form': WikiPageForm}

WikiTemplate = {'schema': WikiTemplateSchema, 'form': WikiTemplateForm}

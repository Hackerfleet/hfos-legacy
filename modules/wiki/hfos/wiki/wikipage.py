"""
Schema: WikiPage
================

Contains
--------

WikiPage: WikiPage to store collaborative data

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import defaultform, editbuttons
from copy import deepcopy
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

WikiPageSchema = base_object('wikipage', roles_read=['crew'])

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

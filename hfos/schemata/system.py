"""
Schema: System
==============

Contains
--------

System: Global systemwide settings

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""
from hfos.schemata.defaultform import savebutton

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


SystemconfigSchema = {
    'id': '#systemconfig',
    'type': 'object',
    'name': 'systemconfig',
    'properties': {
        'uuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique System ID'
        },
        'active': {
            'type': 'boolean', 'title': 'Active configuration',
            'description': 'Determines which configuration will be used. Only one can be active.',
            'default': False
        },
        'name': {
            'type': 'string', 'minLength': 1, 'title': 'Name',
            'description': 'System name'
        },
        'description': {
            'type': 'string', 'format': 'html',
            'title': 'Description',
            'description': 'System description'
        },
        'owneruuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Associated Owner Unique User ID'
        },
        'vesseluuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Associated Vessel Unique ID'
        },
        'defaultmapviewuuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Default Mapview Unique ID'
        },
        'defaultdashboarduuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Default Dashboard Unique ID'
        },
        'defaulttheme': {'type': 'string', 'title': 'Default new client theme',
                         'description': 'Default theme used for user '
                                        'interface'},
    }
}

SystemconfigForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'name', 'theme'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    {'key': 'active', 'readonly': True}, 'locked'
                ]
            }
        ]
    },
    'description',
    savebutton
]

Systemconfig = {'schema': SystemconfigSchema, 'form': SystemconfigForm}

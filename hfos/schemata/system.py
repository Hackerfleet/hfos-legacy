"""
Schema: System
==============

Contains
--------

System: Global systemwide settings

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""
from hfos.schemata.defaultform import savebutton, lookup_field

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

SystemconfigSchema = {
    'id': '#systemconfig',
    'type': 'object',
    'name': 'systemconfig',
    'properties': {
        'uuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique System ID'
        },
        'active': {
            'type': 'boolean', 'title': 'Active configuration',
            'description': 'Determines which configuration will be used. '
                           'Only one can be active.',
            'default': False
        },
        'salt': {
            'type': 'string', 'minLength': 1, 'title': 'Salt',
            'description': 'System hashing salt'
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
        'allowregister': {'type': 'boolean', 'title': 'Registration open',
                          'description': 'Allow self registration of new '
                                         'users'},
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
        'defaulttaskgriduuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Default Taskgrid Unique ID'
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
                    'name'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    {'key': 'active', 'readonly': True}, 'allowregister'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    lookup_field('defaultmapviewuuid', 'mapview'),
                    lookup_field('defaultdashboarduuid', 'dashboardconfig'),
                    lookup_field('defaulttaskgriduuid', 'taskgridconfig')
                ]
            }
        ]
    },

    'description',
    savebutton
]

SystemconfigOptions = {
    'hidden': ['salt']
}

Systemconfig = {'schema': SystemconfigSchema, 'form': SystemconfigForm,
                'options': SystemconfigOptions}

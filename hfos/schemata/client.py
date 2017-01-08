"""
Schema: Client
==============

Contains
--------

Client: Clientprofile to store client specific settings

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""
from hfos.schemata.defaultform import savebutton

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

ClientconfigSchema = {
    'id': '#client',
    'type': 'object',
    'name': 'client',
    'properties': {
        'uuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique Client ID'
            },
        'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
                 'description': 'Client name'},
        'autologin': {'type': 'boolean', 'title': 'Automatic login',
                      'description': 'Automatically logs in this client.'},
        'active': {'type': 'boolean', 'title': 'Active client',
                   'description': 'Indicates whether client is currently '
                                  'active.'},
        'locked': {'type': 'boolean', 'title': 'Locked client',
                   'description': 'Determines whether the client should be '
                                  'locked against changes.'},
        'currentview': {'type': 'string', 'minLength': 1, 'title': 'Name',
                        'description': 'Client name'},
        'theme': {'type': 'string', 'title': 'Client Theme',
                  'description': 'Theme used for user interface'},
        'description': {'type': 'string', 'format': 'html',
                        'title': 'Client description',
                        'description': 'Client description'},
        'useruuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Associated Unique User ID'
            },
        'mapviewuuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Associated Unique Mapview ID'
            },
        'dashboarduuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Associated Unique Dashboard ID'
            },
    }
}

ClientconfigForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'name', 'theme'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    {'key': 'active', 'readonly': True}, 'locked', 'autologin'
                ]
            }
        ]
    },
    {
        'key': 'dashboarduuid',
        'type': 'strapselect',
        'placeholder': 'Select a Dashboard',
        'options': {
            "type": "dashboardconfig",
            "asyncCallback": "$ctrl.getFormData",
            "map": {'valueProperty': "uuid", 'nameProperty': 'name'}
        }
    },
    {
        'key': 'mapviewuuid',
        'type': 'strapselect',
        'placeholder': 'Select a MapView',
        'options': {
            "type": "mapview",
            "asyncCallback": "$ctrl.getFormData",
            "map": {'valueProperty': "uuid", 'nameProperty': 'name'}
        }
    },
    'description',
    savebutton
]

Client = {'schema': ClientconfigSchema, 'form': ClientconfigForm}

__schema__ = ClientconfigSchema
__form__ = ClientconfigForm

"""

Schema: Profile
===============

Contains
--------

Profile: Userprofile with general flags and fields

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""
from hfos.schemata.defaultform import savebutton
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

ProfileSchema = base_object('profile', roles_create='crew')

ProfileSchema['properties'].update({
    'name': {'type': 'string', 'title': 'Name',
             'description': 'Profile name'},
    "userdata": {
        "id": "#profile.userdata",
        "type": "object",
        "properties": {
            'name': {'type': 'string', 'minLength': 1, 'title': 'Name',
                     'description': 'First name'},
            'familyname': {'type': 'string', 'minLength': 1,
                           'title': 'Family Name',
                           'description': 'Last/Family name'},
            'nick': {'type': 'string', 'title': 'nickname',
                     'description': 'Nick/calling name'},
            'location': {'type': 'string',
                         'title': 'Current user location',
                         'description': 'Autoupdated (if possible) user '
                                        'location'},
            'd-o-b': {'type': 'string', 'title': 'Birthday',
                      'format': 'datepicker',
                      'description': 'Date of birth'},
            'phone': {'type': 'string', 'title': 'Telephone number',
                      'description': 'International phone number'},
            'callsign': {'type': 'string', 'title': 'Radio callsign',
                         'description': 'HAM Radio etc callsign'},
            'shift': {'type': 'integer', 'title': 'Selected shift No.',
                      'description': '<a '
                                     'href="#/preferences/shifts">Setup '
                                     'shifts</a>'},
            'visa': {'type': 'boolean', 'title': 'Visas etc',
                     'description': 'Got all Visa documents etc?'},
            'notes': {'type': 'string', 'format': 'html',
                      'title': 'User notes',
                      'description': 'Custom user notes'},
            'image': {'type': 'string'}
        }
    },
    "components": {
        "id": "#profile.components",
        "type": "object",
        "properties": {
            "enabled": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "settings": {
                "type": "array",
                "items": {
                    "id": "#components.settings",
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "settings": {"type": "object"}
                    }
                }
            }
        }
    },
    "settings": {
        "id": "#profile.settings",
        "type": "object",
        "properties": {
            'color': {'type': 'string', 'title': 'User Color',
                      'format': 'color',
                      'description': 'Color used for map annotations, '
                                     'chat etc'},
            'theme': {'type': 'string', 'title': 'User Theme',
                      'description': 'Theme used for user interface'},
            'background': {'type': 'string',
                           'title': 'Background Image',
                           'description': 'Application background image',
                           'default': 'default'},
            'notifications': {
                "id": "#profile.settings.notifications",
                "type": "object",
                "properties": {
                    'delete': {'type': 'boolean', 'title': 'Delete '
                                                           'confirmation',
                               'description': 'Enable confirmation '
                                              'warning on object '
                                              'deletion.',
                               'default': True}
                }
            },
            'notes': {'type': 'string', 'format': 'html',
                      'title': 'Profile notes',
                      'description': 'Custom profile notes'},
            'menu': {
                "type": "array",
                "items": {
                    "id": "menuentry",
                    "title": "Menu entry",
                    "type": "object",
                    "properties": {
                        "title": {"type": "string",
                                  "title": "Menuitem title"},
                        "row": {"type": "integer",
                                "title": "Menuitem row"},
                        "col": {"type": "integer",
                                "title": "Menuitem column"},
                        "size": {"type": "integer",
                                 "title": "Menuitem size"},
                    }
                }
            },
            'mapviewuuid': {
                'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{'
                           '4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                'type': 'string',
                'title': 'Default Unique Mapview ID'
            },
            'taskgriduuid': {
                'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{'
                           '4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                'type': 'string',
                'title': 'Default Unique Taskgrid ID'
            },
            'dashboarduuid': {
                'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{'
                           '4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                'type': 'string',
                'title': 'Default Unique Dashboard ID'
            }
        }
    },
    "alertconfig": {
        "id": "#profile.alertconfig",
        "type": "object",
        "properties": {
            'ontime': {'type': 'string', 'title': 'Active',
                       'description': 'Active alert times'}

        }
    }

})

ProfileForm = [
    'name',
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'help',
                'helpvalue': '<h2>User information</h2>'
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'userdata.name', 'userdata.d-o-b', 'userdata.shift'
                ]
            }, {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'userdata.familyname', 'userdata.callsign',
                    'userdata.location'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-4',
                'items': [
                    'userdata.nick', 'userdata.phone', 'userdata.visa'
                ]
            }
        ]
    },
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'help',
                'helpvalue': '<h2>User interface settings</h2>'
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-3',
                'items': [
                    'settings.color', 'settings.theme'
                ]
            }, {
                'type': 'section',
                'htmlClass': 'col-xs-9',
                'items': [
                    'settings.background'
                ]
            }
        ]
    },
    'settings.notifications',
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'help',
                'helpvalue': '<h2>Default module configurations</h2>'
            },
            {
                'key': 'settings.dashboarduuid',
                'htmlClass': 'col-xs-4',
                'type': 'strapselect',
                'placeholder': 'Select a Dashboard',
                'options': {
                    "type": "dashboardconfig",
                    "asyncCallback": "$ctrl.getFormData",
                    "map": {'valueProperty': "uuid", 'nameProperty': 'name'}
                }
            },
            {
                'key': 'settings.taskgriduuid',
                'htmlClass': 'col-xs-4',
                'type': 'strapselect',
                'placeholder': 'Select a Taskgrid Configuration',
                'options': {
                    "type": "taskgridconfig",
                    "asyncCallback": "$ctrl.getFormData",
                    "map": {'valueProperty': "uuid", 'nameProperty': 'name'}
                }
            },
            {
                'key': 'settings.mapviewuuid',
                'htmlClass': 'col-xs-4',
                'type': 'strapselect',
                'placeholder': 'Select a MapView',
                'options': {
                    "type": "mapview",
                    "asyncCallback": "$ctrl.getFormData",
                    "map": {'valueProperty': "uuid", 'nameProperty': 'name'}
                }
            }
        ],
    },
    'alertconfig',
    'userdata.notes',
    savebutton
]

Profile = {'schema': ProfileSchema, 'form': ProfileForm}

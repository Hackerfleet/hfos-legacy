"""

Schema: Shareable
=================

Contains
--------

Shareable object for common item time sharing management

See also
--------

Provisions

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import editbuttons

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

ShareableSchema = {
    'type': 'object',
    'id': '#shareable',
    'name': 'shareable',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36,
                 'title': 'Unique Shareable ID', 'description': 'HIDDEN'},
        'name': {'type': 'string', 'title': 'Name',
                 'description': 'Name of Shareable', 'unique': True},
        'creatoruuid': {'type': 'string', 'title': 'Creator',
                        'description': 'Creator of Shareable'},
        'created': {'type': 'string', 'format': 'datetimepicker',
                    'title': 'Creation time',
                    'description': 'Time of object creation'},
        'owneruuid': {'type': 'string', 'minLength': 36,
                      'title': "Owner's Unique ID", 'description': 'HIDDEN'},
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
        },
    }
}

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
                        'key': 'owneruuid',
                        'type': 'uiselect',
                        'placeholder': 'Select an Owner',
                        'options': {
                            "type": "user",
                            "asyncCallback": "getFormData",
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
    {
        'key': 'reservations',
        'add': "Add reservation",
        'style': {
            'add': "btn-success"
        },
        'items': [
            'reservations[].title',
            'reservations[].useruuid',
            {
                'type': 'section',
                'htmlClass': 'container-fluid',
                'items': [
                    {
                        'type': 'section',
                        'htmlClass': 'row',
                        'items': [
                            {
                                'htmlClass': 'foobar',
                                'key': 'reservations[].starttime',
                                'options': {
                                    "minuteStep": 15,
                                    "autoclose": 1
                                }
                            },
                            {
                                'htmlClass': 'col-md-2',
                                'key': 'reservations[].endtime',
                                'options': {
                                    "minuteStep": 15,
                                    "autoclose": 1
                                }
                            }
                        ]
                    }
                ]
            },
            'reservations[].description',
        ]
    },
    editbuttons
]

Shareable = {'schema': ShareableSchema, 'form': ShareableForm}

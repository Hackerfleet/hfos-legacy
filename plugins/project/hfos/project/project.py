"""

Schema: Project
============

Contains
--------

Project reference entry for the todo management

See also
--------

Provisions

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from hfos.schemata.defaultform import editbuttons

ProjectSchema = {
    'type': 'object',
    'id': '#project',
    'name': 'project',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36, 'title': 'Unique Project ID', 'description': 'HIDDEN'},
        'name': {'type': 'string', 'title': 'Name', 'description': 'Name of Project', 'unique': True},
        'creatoruuid': {'type': 'string', 'title': 'Creator', 'description': 'Creator of Project'},
        'owneruuid': {'type': 'string', 'minLength': 36, 'title': "Owner's Unique ID", 'description': 'HIDDEN'},
        'priority': {'type': 'number', 'title': 'Priority', 'description': '1 is Highest priority', 'minimum': 1},
        'tags': {'type': 'string', 'title': 'Tags', 'description': 'Attached tags'},
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                  'description': 'Entry notes'}
    }
}

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
                        'key': 'owneruuid',
                        'type': 'uiselect',
                        'placeholder': 'Select an Owner',
                        'options': {
                            "type": "user",
                            "asyncCallback": "getFormData",
                            "map": {'valueProperty': "uuid", 'nameProperty': 'name'}
                        },
                        "onChange": 'fieldChange(modelValue, form)'
                        #                             '''function (modelValue, form) {
                        # $scope.form.forEach(function (item) {
                        # if (item.key == "multiselectDynamicHttpGet") {
                        #     item.options.scope.populateTitleMap(item);
                        # }
                        # });
                        # alert("onChange happened!\nYou changed this value into " + modelValue + " !\nThen code in this event cause the multiselectDynamicHttpGet to reload. \nSee the ASF onChange event for info.");
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
    'owneruuid',
    editbuttons
]

Project = {'schema': ProjectSchema, 'form': ProjectForm}

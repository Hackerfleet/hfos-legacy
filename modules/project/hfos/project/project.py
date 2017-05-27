"""

Schema: Project
============

Contains
--------

Project reference entry for the todo management

See also
--------

Provisions

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import editbuttons
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

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

Project = {'schema': ProjectSchema, 'form': ProjectForm}

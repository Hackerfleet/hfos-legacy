"""

Schema: WateringRule
============

Contains
--------

WateringRule reference entry for the garden to set up pump start times and
durations as well as conditions..

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

WateringRuleSchema = {
    'type': 'object',
    'id': '#',
    'name': 'wateringrule',
    'properties': {
        'uuid': {'type': 'string', 'minLength': 36,
                 'title': 'Unique WateringRule ID', 'description': 'HIDDEN'},
        'name': {'type': 'string', 'title': 'Name',
                 'description': 'Name of WateringRule'},
        'status': {'type': 'bool', 'title': 'Status', 'description':
            'If watering rule is active'},
        'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
                  'description': 'Entry notes'},
        'activationtime': {'type': 'string', 'description': 'Activation time '
                                                            'of watering '
                                                            'rule'},
        'duration': {'type': 'number', 'description': 'Duration of pump '
                                                      'activation'}

    }
}

WateringRuleForm = [
    {
        'type': 'section',
        'htmlClass': 'row',
        'items': [
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'name', 'activationtime'
                ]
            },
            {
                'type': 'section',
                'htmlClass': 'col-xs-6',
                'items': [
                    'status', 'duration'

                ]
            },
        ]
    },
    'notes',
    {
        'key': 'Toggle',
        'type': 'button',
        'onClick': 'formAction("garden", "toggle", model.uuid)',
        'title': 'Toggle WateringRule'
    },
    {
        'key': 'Suspend',
        'type': 'button',
        'condition': 'model.status',
        'onClick': 'formAction("garden", "suspend", model.uuid)',
        'title': 'Suspend the rule for the next time'
    },
    {
        'type': 'submit',
        'title': 'Save Watering Rule',
    }
]

WateringRule = {'schema': WateringRuleSchema, 'form': WateringRuleForm}

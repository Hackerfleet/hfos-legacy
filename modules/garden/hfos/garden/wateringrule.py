"""

Schema: WateringRule
============

Contains
--------

WateringRule reference entry for the garden to set up pump start times and
durations as well as conditions..

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

WateringRuleSchema = base_object('wateringrule', all_roles='crew')

WateringRuleSchema['properties'].update({
    'status': {'type': 'bool', 'title': 'Status', 'description':
        'If watering rule is active'},
    'notes': {'type': 'string', 'format': 'html', 'title': 'User notes',
              'description': 'Entry notes'},
    'activationtime': {'type': 'string', 'description': 'Activation time '
                                                        'of watering '
                                                        'rule'},
    'duration': {'type': 'number', 'description': 'Duration of pump '
                                                  'activation'}
})

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
        'onClick': 'formAction("hfos.garden", "toggle", model.uuid)',
        'title': 'Toggle WateringRule'
    },
    {
        'key': 'Suspend',
        'type': 'button',
        'condition': 'model.status',
        'onClick': 'formAction("hfos.garden", "suspend", model.uuid)',
        'title': 'Suspend the rule for the next time'
    },
    {
        'type': 'submit',
        'title': 'Save Watering Rule',
    }
]

WateringRule = {'schema': WateringRuleSchema, 'form': WateringRuleForm}

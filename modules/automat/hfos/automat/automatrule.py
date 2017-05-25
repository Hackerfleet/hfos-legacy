"""
Schema: Automatrule
=====================

Contains
--------

Automat: Structure to store automat configurations

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import *
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

AutomatRuleSchema = base_object('automatrule', all_roles='crew')

AutomatRuleSchema['properties'].update({

    'output': {
        'type': 'object',
        'properties': {
            'event': {
                'type': 'object',
                'properties': {
                    'destination': {
                        'type': 'string',
                        'title': 'Destination',
                        'description': 'Destination of output event'
                    },
                    'name': {
                        'type': 'string',
                        'title': 'Event name',
                        'description': 'Name of output event'
                    }
                }
            },
            'data': {
                'type': 'string'
            }
        }
    },
    'input': {
        'type': 'object',
        'properties': {
            'event': {
                'type': 'object',
                'properties': {
                    'source': {
                        'type': 'string',
                        'title': 'Source',
                        'description': 'Source of input event'
                    },
                    'name': {
                        'type': 'string',
                        'title': 'Event name',
                        'description': 'Name of input event'
                    }
                }
            },
            'logic': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'field': {
                            'type': 'string',
                            'title': 'Field',
                            'description': 'Field for condition'
                        },
                        'tool': {
                            'type': 'string',
                            'title': 'Tool',
                            'description': 'Condition analysis tool'
                        },
                        'function': {
                            'type': 'string',
                            'title': 'Function',
                            'description': 'Function of tool'
                        },
                        'argument': {
                            'type': 'string',
                            'title': 'Argument',
                            'description': 'Argument for tool'
                        }
                    }
                }
            }
        }
    },
    'enabled': {
        'type': 'boolean',
        'title': 'Enabled',
        'description': 'Is Rule enabled?'
    }
})

AutomatForm = noform

AutomatRule = {'schema': AutomatRuleSchema, 'form': AutomatForm}

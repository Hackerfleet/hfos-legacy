#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2017 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "GPLv3"

"""
Schema: Automatrule
===================

Contains
--------

AutomatRule: Structure to store automat rule configurations


"""

from hfos.schemata.defaultform import *
from hfos.schemata.base import base_object

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
                        'description': 'Destination of output event',
                        'default': ''
                    },
                    'name': {
                        'type': 'string',
                        'title': 'Event name',
                        'description': 'Name of output event',
                        'default': ''
                    }
                }
            },
            'data': {
                'type': 'object',
                'default': {}
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
                        'description': 'Source of input event',
                        'default': ''
                    },
                    'name': {
                        'type': 'string',
                        'title': 'Event name',
                        'description': 'Name of input event',
                        'default': ''
                    }
                }
            },
            'logic': {
                'type': 'array',
                'default': [],
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
                            'oneOf': [
                                {
                                    'type': 'string',
                                    'title': 'Argument',
                                    'description': 'Text Argument for tool'
                                },
                                {
                                    'type': 'integer',
                                    'title': 'Argument',
                                    'description': 'Integer Argument for tool'
                                }
                            ]
                        }
                    }
                }
            }
        }
    },
    'enabled': {
        'type': 'boolean',
        'title': 'Enabled',
        'description': 'Is Rule enabled?',
        'default': False
    }
})

AutomatForm = noform

AutomatRule = {'schema': AutomatRuleSchema, 'form': AutomatForm}

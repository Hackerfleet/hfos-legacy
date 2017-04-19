"""
Schema: Controllable
====================

Contains
--------

Controllable: Patterns of remote control

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import defaultform
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

ControllableSchema = base_object('controllable')

ControllableSchema['properties'].update({
    'description': {'type': 'string'},
    'type': {'enum': ['analog', 'digital']},
    'min': {'type': 'integer', 'default': 0},
    'center': {'type': 'integer', 'default': 127},
    'max': {'type': 'integer', 'default': 255},
})

Controllable = {'schema': ControllableSchema, 'form': defaultform}

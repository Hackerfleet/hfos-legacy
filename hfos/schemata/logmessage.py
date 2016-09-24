"""
Schema: Log Message
==============

Contains
--------

LogMessage: LogMessage to store messages in rooms and private logs

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import readonlyform

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

LogMessageSchema = {
    'id': '#logmessage',
    'type': 'object',
    'name': 'logmessage',
    'properties': {
        'uuid': {
            'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-['
                       'a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
            'type': 'string',
            'title': 'Unique Log Message ID'
            },
        'timestamp': {'type': 'number', 'title': 'Timestamp',
                      'description': 'Log Message timestamp (\xc2Sec)'},
        'emitter': {'type': 'string', 'minLength': 1, 'title': 'Emitter',
                    'description': 'Log Message emitter name'},
        'sourceloc': {'type': 'string', 'minLength': 1, 'title': 'Source '
                                                                 'location',
                      'description': 'Log Message source code location'},
        'level': {'type': 'string', 'minLength': 1, 'title': 'Level',
                  'description': 'Log Message elevation level'},
        'content': {'type': 'string', 'minLength': 1, 'title': 'Content',
                    'description': 'Log Message content'}
    }
}

LogMessage = {'schema': LogMessageSchema, 'form': readonlyform}

"""
Schema: Log Message
==============

Contains
--------

LogMessage: LogMessage to store messages in rooms and private logs

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from hfos.schemata.defaultform import readonlyform

LogMessageSchema = {
    'id': '#logmessage',
    'type': 'object',
    'name': 'logmessage',
    'properties': {
        'uuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
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

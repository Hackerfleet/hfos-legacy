"""
Schema: Chat Message
==============

Contains
--------

ChatMessage: ChatMessage to store messages in rooms and private chats

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import defaultform

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

ChatMessageSchema = {
    'id': '#chatmessage',
    'type': 'object',
    'name': 'chatmessage',
    'properties': {
        'timestamp': {'type': 'string', 'title': 'Timestamp',
                      'format': 'datetimepicker',
                      'description': 'Message timestamp'},
        'recipient': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{'
                                 '4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                      'type': 'string',
                      'title': 'Unique User ID of recipient'
                      },
        'sender': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{'
                              '4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                   'type': 'string',
                   'title': 'Unique User ID of sender'
                   },
        'content': {'type': 'string', 'minLength': 1, 'title': 'Name',
                    'description': 'Chat Message name'}
    }
}

ChatMessage = {'schema': ChatMessageSchema, 'form': defaultform}

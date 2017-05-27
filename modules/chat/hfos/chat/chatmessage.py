"""
Schema: Chat Message
==============

Contains
--------

ChatMessage: ChatMessage to store messages in rooms and private chats

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.schemata.defaultform import defaultform
from hfos.schemata.base import base_object

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

ChatMessageSchema = base_object('chatmessage', all_roles='crew')

ChatMessageSchema['properties'].update({
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
})

ChatMessage = {'schema': ChatMessageSchema, 'form': defaultform}

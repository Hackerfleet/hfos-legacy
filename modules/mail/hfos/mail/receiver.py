#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2018 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""


Module MailReceiver
===================


"""

from hfos.component import ConfigurableComponent, handler
from hfos.logger import hfoslog, events, verbose, debug, warn, critical, error, hilight


class MailReceiver(ConfigurableComponent):
    """Receives mails on multiple accounts"""

    configprops = {
        'receive_mail': {
            'type': 'boolean',
            'title': 'Receive mail',
            'description': 'Poll configured accounts for new mail',
            'default': True
        },
        'accounts': {
            'type': 'array',
            'items': {
                'properties': {
                    'server': {
                        'type': 'string',
                        'title': 'Mail server',
                        'description': 'Mail server to receive emails from',
                        'default': 'localhost'
                    },
                    'server_port': {
                        'type': 'integer',
                        'title': 'Mail server port',
                        'description': 'Mail server port to connect to',
                        'default': 993
                    },
                    'ssl': {
                        'type': 'boolean',
                        'title': 'Use SSL',
                        'description': 'Use SSL to secure the mail server connection',
                        'default': True
                    },
                    'tls': {
                        'type': 'boolean',
                        'title': 'Use TLS',
                        'description': 'Use TLS to secure the mail server connection',
                        'default': False
                    },
                    'protocol': {
                        'type': 'string',
                        'title': 'Server protocol',
                        'description': 'Protocol to use with this mail server',
                        'default': 'imap',
                        'enum': ['imap', 'pop3']
                    },
                    'username': {
                        'type': 'string',
                        'title': 'Username',
                        'default': ''
                    },
                    'password': {
                        'type': 'string',
                        'title': 'Password',
                        'x-schema-form': {
                            'type': 'password'
                        }
                    },

                }
            }
        }
    }

    def __init__(self, *args, **kwargs):
        super(MailReceiver, self).__init__('MAILRX', *args, **kwargs)

        self.log("Started")
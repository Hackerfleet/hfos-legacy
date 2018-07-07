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
Client Objects
==============

Contains
--------

Socket:
Client:
User:


"""

from hfos.misc import std_human_uid


class Socket(object):
    """
    Socket metadata object
    """

    def __init__(self, ip, clientuuid):
        """

        :param ip: Associated Internet protocol address
        :param clientuuid: Unique Uniform ID of this client
        """
        super(Socket, self).__init__()
        self.ip = ip
        self.clientuuid = clientuuid


class Client(object):
    """
    Client metadata object
    """

    def __init__(self, sock, ip, clientuuid, useruuid=None, name='',
                 config=None):
        """

        :param sock: Associated connection
        :param ip: Associated Internet protocol address
        :param clientuuid: Unique Uniform ID of this client
        """
        super(Client, self).__init__()

        self.sock = sock
        self.ip = ip
        self.uuid = clientuuid
        self.useruuid = useruuid
        if name == '':
            self.name = std_human_uid(kind='place')
        else:
            self.name = name
        self.config = config

    def __repr__(self):
        return self.name


class User(object):
    """
    Authenticated clients with profile etc
    """

    def __init__(self, account, profile, uuid):
        """

        :param account: userobject
        :param profile: profileobject
        :param uuid: profileobject
        """

        super(User, self).__init__()
        self.clients = []
        self.uuid = uuid
        self.profile = profile
        self.account = account

    def __repr__(self):
        return str(self.account)

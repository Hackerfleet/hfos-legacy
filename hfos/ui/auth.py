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

Module: Auth
============

Authentication (and later Authorization) system


"""

from uuid import uuid4
from circuits import Event, Timer

from hfos.component import handler
from hfos.events.client import authentication, send
from hfos.component import ConfigurableComponent
from hfos.database import objectmodels
from hfos.logger import error, warn, debug
from hfos.misc import std_hash, std_salt, std_uuid, std_now, std_human_uid


class AuthenticationError(Exception):
    """Something unspecified went wrong during authentication"""
    pass


class add_auth_hook(Event):
    """Allows for adding event hooks to the authentication process"""

    def __init__(self, authenticator_name, event, *args, **kwargs):
        super(add_auth_hook, self).__init__(*args, **kwargs)
        self.authenticator_name = authenticator_name
        self.event = event


class Authenticator(ConfigurableComponent):
    """
    Authenticates users against the database.
    """

    channel = "hfosweb"

    configprops = {}

    def __init__(self, *args):
        super(Authenticator, self).__init__('AUTH', *args)
        # self.log(objectmodels['systemconfig'], lvl=error)

        self.failing_clients = {}

        systemconfig = objectmodels['systemconfig'].find_one({'active': True})

        # TODO: Decouple systemconfig creation from authenticator
        try:
            salt = systemconfig.salt.encode('ascii')
            self.log('Using active systemconfig salt')
        except (KeyError, AttributeError):
            self.log('No active system configuration found!', lvl=error)
            salt = std_salt().encode('ascii')

        self.salt = salt
        self.systemconfig = systemconfig

        self.auth_hooks = {}

    @handler("add_auth_hook")
    def add_auth_hook(self, event):
        """Register event hook on reception of add_auth_hook-event"""

        self.log('Adding authentication hook for', event.authenticator_name)
        self.auth_hooks[event.authenticator_name] = event.event

    def _fail(self, event, message='Invalid credentials'):
        """Sends a failure message to the requesting client"""

        notification = {
            'component': 'auth',
            'action': 'fail',
            'data': message
        }

        ip = event.sock.getpeername()[0]

        self.failing_clients[ip] = event
        Timer(3, Event.create('notify_fail', event.clientuuid, notification, ip)).register(self)

    def notify_fail(self, uuid, notification, ip):
        self.log('Transmitting delayed fail notification', lvl=debug)
        self.fireEvent(send(uuid, notification, sendtype='client'))
        del self.failing_clients[ip]

    def _login(self, event, user_account, user_profile, client_config):
        """Send login notification to client"""

        user_account.lastlogin = std_now()
        user_account.save()

        user_account.passhash = ""
        self.fireEvent(
            authentication(user_account.name, (
                user_account, user_profile, client_config),
                           event.clientuuid,
                           user_account.uuid,
                           event.sock),
            "auth")

    @handler("authenticationrequest", channel="auth")
    def authenticationrequest(self, event):
        """Handles authentication requests from clients
        :param event: AuthenticationRequest with user's credentials
        """

        if event.sock.getpeername()[0] in self.failing_clients:
            self.log('Client failed a login and has to wait', lvl=debug)
            return

        if event.auto:
            self._handle_autologin(event)
        else:
            self._handle_login(event)

    def _handle_autologin(self, event):
        """Automatic logins for client configurations that allow it"""

        self.log("Verifying automatic login request")

        # TODO: Check for a common secret

        # noinspection PyBroadException
        try:
            client_config = objectmodels['client'].find_one({
                'uuid': event.requestedclientuuid
            })
        except Exception:
            client_config = None

        if client_config is None or client_config.autologin is False:
            self.log("Autologin failed:", event.requestedclientuuid,
                     lvl=error)
            self._fail(event)
            return

        try:
            user_account = objectmodels['user'].find_one({
                'uuid': client_config.owner
            })
            if user_account is None:
                raise AuthenticationError
            self.log("Autologin for", user_account.name, lvl=debug)
        except Exception as e:
            self.log("No user object due to error: ", e, type(e),
                     lvl=error)
            self._fail(event)
            return

        if user_account.active is False:
            self.log("Account deactivated.")
            self._fail(event, 'Account deactivated.')
            return

        user_profile = self._get_profile(user_account)

        self._login(event, user_account, user_profile, client_config)

        self.log("Autologin successful!", lvl=warn)

    def _handle_login(self, event):
        """Manual password based login"""

        # TODO: Refactor to simplify

        self.log("Auth request for ", event.username, 'client:',
                 event.clientuuid)

        # TODO: Define the requirements for secure passwords etc.
        # They're also required in the Enrol module..!

        if (len(event.username) < 1) or (len(event.password) < 5):
            self.log("Illegal username or password received, login cancelled", lvl=warn)
            self._fail(event, 'Password or username too short')
            return

        client_config = None

        try:
            user_account = objectmodels['user'].find_one({
                'name': event.username
            })
            # self.log("Account: %s" % user_account._fields, lvl=debug)
            if user_account is None:
                raise AuthenticationError
        except Exception as e:
            self.log("No userobject due to error: ", e, type(e),
                     lvl=error)
            self._fail(event)
            return

        self.log("User found.", lvl=debug)

        if user_account.active is False:
            self.log("Account deactivated.")
            self._fail(event, 'Account deactivated.')
            return

        if not std_hash(event.password, self.salt) == user_account.passhash:
            self.log("Password was wrong!", lvl=warn)
            self._fail(event)
            return

        self.log("Passhash matches, checking client and profile.",
                 lvl=debug)

        requested_client_uuid = event.requestedclientuuid
        if requested_client_uuid is not None:
            client_config = objectmodels['client'].find_one({
                'uuid': requested_client_uuid
            })

        if client_config:
            self.log("Checking client configuration permissions",
                     lvl=debug)
            # TODO: Shareable client configurations?
            if client_config.owner != user_account.uuid:
                client_config = None
                self.log("Unauthorized client configuration "
                         "requested",
                         lvl=warn)
        else:
            self.log("Unknown client configuration requested: ",
                     requested_client_uuid, event.__dict__,
                     lvl=warn)

        if not client_config:
            self.log("Creating new default client configuration")
            # Either no configuration was found or not requested
            # -> Create a new client configuration
            uuid = event.clientuuid if event.clientuuid is not None else str(uuid4())

            client_config = objectmodels['client']({'uuid': uuid})

            client_config.name = std_human_uid(kind='place')

            client_config.description = "New client configuration from " + user_account.name
            client_config.owner = user_account.uuid

            # TODO: Get client configuration storage done right, this one is too simple
            client_config.save()

        user_profile = self._get_profile(user_account)

        self._login(event, user_account, user_profile, client_config)
        self.log("Done with Login request", lvl=debug)

    def _get_profile(self, user_account):
        """Retrieves a user's profile"""

        try:
            # TODO: Load active profile, not just any
            user_profile = objectmodels['profile'].find_one(
                {'owner': str(user_account.uuid)})
            self.log("Profile: ", user_profile,
                     user_account.uuid, lvl=debug)
        except Exception as e:
            self.log("No profile due to error: ", e, type(e),
                     lvl=error)
            user_profile = None

        if not user_profile:
            default = {
                'uuid': std_uuid(),
                'owner': user_account.uuid,
                'userdata': {
                    'notes': 'Default profile of ' + user_account.name
                }
            }
            user_profile = objectmodels['profile'](default)
            user_profile.save()

        return user_profile

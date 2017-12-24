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

Module: Auth
============

Authentication (and later Authorization) system


"""

from uuid import uuid4
from hashlib import sha512
from circuits import Event

from hfos.component import handler
from hfos.events.client import authentication, send
from hfos.events.system import authorizedevent
from hfos.component import ConfigurableComponent
from hfos.database import objectmodels, makesalt
from hfos.logger import error, warn, debug, verbose


class add_auth_hook(Event):
    """Allows for adding event hooks to the authentication process"""

    def __init__(self, authenticator_name, event, *args, **kwargs):
        super(add_auth_hook, self).__init__(*args, **kwargs)
        self.authenticator_name = authenticator_name
        self.event = event


class changepassword(authorizedevent):
    pass


class Authenticator(ConfigurableComponent):
    """
    Authenticates users against the database.
    """

    channel = "hfosweb"

    configprops = {}

    def __init__(self, *args):
        super(Authenticator, self).__init__('AUTH', *args)
        # self.log(objectmodels['systemconfig'], lvl=error)

        systemconfig = objectmodels['systemconfig'].find_one({'active': True})

        # TODO: Decouple systemconfig creation from authenticator
        try:
            salt = systemconfig.salt.encode('ascii')
            self.log('Using active systemconfig salt')
        except (KeyError, AttributeError):
            self.log('No active system configuration found!', lvl=error)
            salt = makesalt().encode('ascii')

        self.salt = salt
        self.systemconfig = systemconfig

        self.auth_hooks = {}

    def makehash(self, word):
        """Generates a cryptographically strong (sha512) hash with this nodes
        salt added."""

        try:
            password = word.encode('utf-8')
        except UnicodeDecodeError:
            password = word

        hashword = sha512(password)
        hashword.update(self.salt)
        hex_hash = hashword.hexdigest()

        return hex_hash

    @handler("add_auth_hook")
    def add_auth_hook(self, event):
        """Register event hook on reception of add_auth_hook-event"""

        self.log('Adding authentication hook for', event.authenticator_name)
        self.auth_hooks[event.authenticator_name] = event.event

    @handler("authenticationrequest", channel="auth")
    def authenticationrequest(self, event):
        """Handles authentication requests from clients
        :param event: AuthenticationRequest with user's credentials
        """

        # TODO: Refactor to simplify

        if event.auto:
            self.log("Verifying automatic login request")

            # noinspection PyBroadException
            try:
                clientconfig = objectmodels['client'].find_one({
                    'uuid': event.requestedclientuuid
                })
            except Exception:
                clientconfig = None

            if clientconfig is None or clientconfig.autologin is False:
                self.log("Autologin failed:", event.requestedclientuuid,
                         lvl=error)
                return

            if clientconfig.autologin is True:

                try:
                    useraccount = objectmodels['user'].find_one({
                        'uuid': clientconfig.owner
                    })
                    self.log("Autologin for", useraccount.name, lvl=debug)
                except Exception as e:
                    self.log("No user object due to error: ", e, type(e),
                             lvl=error)

                try:
                    userprofile = objectmodels['profile'].find_one({
                        'owner': str(useraccount.uuid)
                    })
                    self.log("Profile: ", userprofile,
                             useraccount.uuid, lvl=debug)

                    useraccount.passhash = ""
                    self.fireEvent(
                        authentication(useraccount.name, (
                            useraccount, userprofile, clientconfig),
                                       event.clientuuid,
                                       useraccount.uuid,
                                       event.sock),
                        "auth")
                    self.log("Autologin successful!", lvl=warn)
                except Exception as e:
                    self.log("No profile due to error: ", e, type(e),
                             lvl=error)
        else:
            self.log("Auth request for ", event.username,
                     event.clientuuid)

            # TODO: Move registration to its own part
            # TODO: Define the requirements for secure passwords etc.

            if (len(event.username) < 3) or (len(event.password) < 3):
                self.log("Illegal username or password received, "
                         "login cancelled",
                         lvl=warn)
                notification = {
                    'component': 'auth',
                    'action': 'fail',
                    'data': 'Password or username too short'
                }
                self.fireEvent(send(event.clientuuid, notification,
                                    sendtype='client'))
                return

            useraccount = None
            clientconfig = None
            userprofile = None

            # TODO: Notify problems here back to the frontend
            try:
                useraccount = objectmodels['user'].find_one({
                    'name': event.username
                })
                self.log("Account: %s" % useraccount._fields, lvl=debug)
            except Exception as e:
                self.log("No userobject due to error: ", e, type(e),
                         lvl=error)

            if useraccount:
                self.log("User found.", lvl=debug)

                if self.makehash(event.password) == useraccount.passhash:
                    self.log("Passhash matches, checking client and profile.",
                             lvl=debug)

                    requestedclientuuid = event.requestedclientuuid

                    # Client requests to get an existing client
                    # configuration or has none

                    clientconfig = objectmodels['client'].find_one({
                        'uuid': requestedclientuuid
                    })

                    if clientconfig:
                        self.log("Checking client configuration permissions",
                                 lvl=debug)
                        if clientconfig.owner != useraccount.uuid:
                            clientconfig = None
                            self.log("Unauthorized client configuration "
                                     "requested",
                                     lvl=warn)
                    else:
                        self.log("Unknown client configuration requested: ",
                                 requestedclientuuid, event.__dict__,
                                 lvl=warn)

                    if not clientconfig:
                        self.log("Creating new default client configuration")
                        # Either no configuration was found or requested
                        # -> Create a new client configuration
                        uuid = event.clientuuid if event.clientuuid is not \
                                                   None else str(uuid4())

                        clientconfig = objectmodels['client']({'uuid': uuid})

                        clientconfig.name = "New client"
                        clientconfig.description = "New client configuration" \
                                                   " from " + useraccount.name
                        clientconfig.owner = useraccount.uuid
                        # TODO: Make sure the profile is only saved if the
                        # client could store it, too
                        clientconfig.save()

                    try:
                        userprofile = objectmodels['profile'].find_one(
                            {'owner': str(useraccount.uuid)})
                        self.log("Profile: ", userprofile,
                                 useraccount.uuid, lvl=debug)

                        useraccount.passhash = ""
                        self.fireEvent(
                            authentication(useraccount.name, (
                                useraccount, userprofile, clientconfig),
                                           event.clientuuid,
                                           useraccount.uuid,
                                           event.sock),
                            "auth")
                    except Exception as e:
                        self.log("No profile due to error: ", e, type(e),
                                 lvl=error)
                else:
                    self.log("Password was wrong!", lvl=warn)

                    self.fireEvent(send(event.clientuuid, {
                        'component': 'auth',
                        'action': 'fail',
                        'data': 'N/A'
                    }, sendtype="client"), "hfosweb")

                self.log("Done with Login request", lvl=debug)

            elif self.systemconfig.allowregister:
                self.createuser(event)
            else:
                self.log('User not found and system configuration does not '
                         'allow new users to be created', lvl=warn)

    def createuser(self, event):
        """Create a new user and all initial data"""

        self.log("Creating user")
        try:
            newuser = objectmodels['user']({
                'name': event.username,
                'passhash': self.makehash(event.password),
                'uuid': str(uuid4())
            })
            newuser.save()
        except Exception as e:
            self.log("Problem creating new user: ", type(e), e,
                     lvl=error)
            return
        try:
            newprofile = objectmodels['profile']({
                'uuid': str(uuid4()),
                'owner': newuser.uuid
            })
            self.log("New profile uuid: ", newprofile.uuid,
                     lvl=verbose)

            # TODO: Fix this - yuk!
            newprofile.components = {
                'enabled': ["dashboard", "map", "weather", "settings"]}
            newprofile.save()
        except Exception as e:
            self.log("Problem creating new profile: ", type(e),
                     e, lvl=error)
            return

        try:
            # TODO: Clone or reference systemwide default configuration
            uuid = event.clientuuid if event.clientuuid is not None else str(
                uuid4())

            newclientconfig = objectmodels['client']({'uuid': uuid})
            newclientconfig.name = "New client"
            newclientconfig.description = "New client configuration " \
                                          "from " + newuser.name
            newclientconfig.owner = newuser.uuid
            newclientconfig.save()
        except Exception as e:
            self.log("Problem creating new clientconfig: ",
                     type(e), e, lvl=error)
            return

        try:
            self.fireEvent(
                authentication(newuser.name,
                               (newuser, newprofile, newclientconfig),
                               event.clientuuid,
                               newuser.uuid,
                               event.sock),
                "auth")
            self.fireEvent(send(event.clientuuid, {
                'component': 'auth',
                'action': 'new',
                'data': 'registration successful'
            }, sendtype="client"), "hfosweb")
        except Exception as e:
            self.log("Error during new account confirmation transmission",
                     e, lvl=error)

    def profilerequest(self, event):
        """Handles client profile actions
        :param event:
        """

        self.log("Profile update %s" % event)

        if event.action != "update":
            self.log("Unsupported profile action: ", event, lvl=warn)
            return

        try:
            newprofile = event.data
            self.log("Updating with %s " % newprofile, lvl=debug)

            userprofile = objectmodels['profile'].find_one({
                'uuid': event.user.uuid
            })

            self.log("Updating %s" % userprofile, lvl=debug)

            userprofile.update(newprofile)
            userprofile.save()

            self.log("Profile stored.")
            # TODO: Give client feedback
        except Exception as e:
            self.log("General profile request error %s %s" % (type(e), e),
                     lvl=error)

    @handler(changepassword)
    def changepassword(self, event):
        old = event.data['old']
        new = event.data['new']
        uuid = event.user.uuid

        user = objectmodels['user'].find_one({'uuid': uuid})
        if self.makehash(old) == user.passhash:
            user.passhash = self.makehash(new)
            packet = {
                'component': 'hfos.ui.auth',
                'action': 'changepassword',
                'data': True
            }
            self.fireEvent(send(event.client.uuid, packet))
            self.log('Successfully changed password for user', uuid)
        else:
            packet = {
                'component': 'hfos.ui.auth',
                'action': 'changepassword',
                'data': False
            }
            self.fireEvent(send(event.client.uuid, packet))
            self.log('User tried to change password without supplying old one', lvl=warn)

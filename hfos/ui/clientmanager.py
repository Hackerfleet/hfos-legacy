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


Module clientmanager
====================

Coordinates clients communicating via websocket


"""

import datetime
import json

from time import time
from collections import namedtuple
from uuid import uuid4
from base64 import b64decode

from hfos.component import handler
from circuits.net.events import write
from circuits import Event, Timer
from hfos.events.system import get_anonymous_events, get_user_events, authorizedevent
from hfos.events.client import authenticationrequest, send, clientdisconnect, \
    userlogin, userlogout
from hfos.component import ConfigurableComponent
from hfos.database import objectmodels
from hfos.logger import error, warn, critical, debug, info, network, \
    verbose, hilight
from hfos.ui.clientobjects import Socket, Client, User
from hfos.debugger import cli_register_event
from hfos.tools import std_table


class cli_users(Event):
    """Display the list of connected users from the clientmanager"""
    pass


class cli_clients(Event):
    """Display the list of connected clients from the clientmanager"""
    pass


class cli_client(Event):
    """Display detailed info about a connected client"""
    pass


class cli_events(Event):
    """Display the list of authorized and anonymous events"""
    pass


class cli_sources(Event):
    """Display the list of authorized and anonymous events"""
    pass


class cli_who(Event):
    """Display the list of all users and clients"""
    pass


class reset_flood_counters(Event):
    pass


class reset_flood_offenders(Event):
    pass


# Ping for latency measurement

class ping(authorizedevent):
    pass


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.time, datetime.date)):
            return obj.isoformat()
            # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


class ClientManager(ConfigurableComponent):
    """
    Handles client connections and requests as well as client-outbound
    communication.
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(ClientManager, self).__init__('CM', *args)

        self._clients = {}
        self._sockets = {}
        self._users = {}
        self._count = 0
        self._usermapping = {}
        self._flooding = {}
        self._flood_counter = {}

        self.authorized_events = {}
        self.anonymous_events = {}

        self.fireEvent(cli_register_event('users', cli_users))
        self.fireEvent(cli_register_event('clients', cli_clients))
        self.fireEvent(cli_register_event('client', cli_client))
        self.fireEvent(cli_register_event('events', cli_events))
        self.fireEvent(cli_register_event('sources', cli_sources))
        self.fireEvent(cli_register_event('who', cli_who))

        self._flood_counters_resetter = Timer(
            2, Event.create('reset_flood_counters'), persist=True
        ).register(self)
        self._flood_offender_resetter = Timer(
            10, Event.create('reset_flood_offenders'), persist=True
        ).register(self)

    @handler('cli_client')
    def client_details(self, *args):
        """Display known details about a given client"""
        client = self._clients[args[0]]

        self.log(client.uuid, client.ip, client.name, client.useruuid, pretty=True)

    @handler('cli_clients')
    def client_list(self, *args):
        """Display a list of connected clients"""
        if len(self._clients) == 0:
            self.log('No clients connected')
        else:
            self.log(self._clients, pretty=True)

    @handler('cli_users')
    def users_list(self, *args):
        """Display a list of connected users"""
        if len(self._users) == 0:
            self.log('No users connected')
        else:
            self.log(self._users, pretty=True)

    @handler('cli_sources')
    def sourcess_list(self, *args):
        """Display a list of all registered events"""

        from pprint import pprint

        sources = {}
        sources.update(self.authorized_events)
        sources.update(self.anonymous_events)

        for source in sources:
            pprint(source)

    @handler('cli_events')
    def events_list(self, *args):
        """Display a list of all registered events"""

        def merge(a, b, path=None):
            "merges b into a"
            if path is None: path = []
            for key in b:
                if key in a:
                    if isinstance(a[key], dict) and isinstance(b[key], dict):
                        merge(a[key], b[key], path + [str(key)])
                    elif a[key] == b[key]:
                        pass  # same leaf value
                    else:
                        raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
                else:
                    a[key] = b[key]
            return a

        events = {}
        sources = merge(self.authorized_events, self.anonymous_events)

        for source, source_events in sources.items():
            events[source] = []
            for item in source_events:
                events[source].append(item)

        self.log(events, pretty=True)

    @handler('cli_who')
    def who(self, *args):
        """Display a table of connected users and clients"""
        if len(self._users) == 0:
            self.log('No users connected')
            if len(self._clients) == 0:
                self.log('No clients connected')
                return

        Row = namedtuple("Row", ['User', 'Client', 'IP'])
        rows = []

        for user in self._users.values():
            for key, client in self._clients.items():
                if client.useruuid == user.uuid:
                    row = Row(user.account.name, key, client.ip)
                    rows.append(row)

        for key, client in self._clients.items():
            if client.useruuid is None:
                row = Row('ANON', key, client.ip)
                rows.append(row)

        self.log("\n" + std_table(rows))

    @handler('ready')
    def ready(self):
        """Compile events"""

        self.authorized_events = get_user_events()
        self.anonymous_events = get_anonymous_events()

    @handler("disconnect", channel="wsserver")
    def disconnect(self, sock):
        """Handles socket disconnections"""

        self.log("Disconnect ", sock)

        try:
            if sock in self._sockets:
                self.log("Getting socket", lvl=debug)
                sockobj = self._sockets[sock]
                self.log("Getting clientuuid", lvl=debug)
                clientuuid = sockobj.clientuuid
                self.log("getting useruuid", lvl=debug)
                useruuid = self._clients[clientuuid].useruuid

                self.log("Firing disconnect event", lvl=debug)
                self.fireEvent(clientdisconnect(clientuuid, self._clients[
                    clientuuid].useruuid))

                self.log("Logging out relevant client", lvl=debug)
                if useruuid is not None:
                    self.log("Client was logged in", lvl=debug)
                    try:
                        self._logoutclient(useruuid, clientuuid)
                        self.log("Client logged out", useruuid, clientuuid)
                    except Exception as e:
                        self.log("Couldn't clean up logged in user! ",
                                 self._users[useruuid], e, type(e),
                                 lvl=critical)
                self.log("Deleting Client (", self._clients.keys, ")",
                         lvl=debug)
                del self._clients[clientuuid]
                self.log("Deleting Socket", lvl=debug)
                del self._sockets[sock]
        except Exception as e:
            self.log("Error during disconnect handling: ", e, type(e),
                     lvl=critical)

    def _logoutclient(self, useruuid, clientuuid):
        """Log out a client and possibly associated user"""

        self.log("Cleaning up client of logged in user.")
        try:
            self._users[useruuid].clients.remove(clientuuid)
            if len(self._users[useruuid].clients) == 0:
                self.log("Last client of user disconnected.")

                self.fireEvent(userlogout(useruuid, clientuuid))
                del self._users[useruuid]

            self._clients[clientuuid].useruuid = None
        except Exception as e:
            self.log("Error during client logout: ", e, type(e),
                     clientuuid, useruuid, lvl=error,
                     exc=True)

    @handler("connect", channel="wsserver")
    def connect(self, *args):
        """Registers new sockets and their clients and allocates uuids"""

        self.log("Connect ", args, lvl=verbose)

        try:
            sock = args[0]
            ip = args[1]

            if sock not in self._sockets:
                self.log("New client connected:", ip, lvl=debug)
                clientuuid = str(uuid4())
                self._sockets[sock] = Socket(ip, clientuuid)
                # Key uuid is temporary, until signin, will then be replaced
                #  with account uuid

                self._clients[clientuuid] = Client(
                    sock=sock,
                    ip=ip,
                    clientuuid=clientuuid,
                )

                self.log("Client connected:", clientuuid, lvl=debug)
            else:
                self.log("Old IP reconnected!", lvl=warn)
                #     self.fireEvent(write(sock, "Another client is
                # connecting from your IP!"))
                #     self._sockets[sock] = (ip, uuid.uuid4())
        except Exception as e:
            self.log("Error during connect: ", e, type(e), lvl=critical)

    def send(self, event):
        """Sends a packet to an already known user or one of his clients by
        UUID"""

        try:
            jsonpacket = json.dumps(event.packet, cls=ComplexEncoder)
            if event.sendtype == "user":
                # TODO: I think, caching a user name <-> uuid table would
                # make sense instead of looking this up all the time.

                if event.uuid is None:
                    userobject = objectmodels['user'].find_one({
                        'name': event.username
                    })
                else:
                    userobject = objectmodels['user'].find_one({
                        'uuid': event.uuid
                    })

                if userobject is None:
                    self.log("No user by that name known.", lvl=warn)
                    return
                else:
                    uuid = userobject.uuid

                self.log("Broadcasting to all of users clients: '%s': '%s" % (
                    uuid, str(event.packet)[:20]), lvl=network)
                if uuid not in self._users:
                    self.log("User not connected!", event, lvl=critical)
                    return
                clients = self._users[uuid].clients

                for clientuuid in clients:
                    sock = self._clients[clientuuid].sock

                    if not event.raw:
                        self.log("Sending json to client", jsonpacket[:50],
                                 lvl=network)

                        self.fireEvent(write(sock, jsonpacket), "wsserver")
                    else:
                        self.log("Sending raw data to client")
                        self.fireEvent(write(sock, event.packet), "wsserver")
            else:  # only to client
                self.log("Sending to user's client: '%s': '%s'" % (
                    event.uuid, jsonpacket[:20]), lvl=network)
                if event.uuid not in self._clients:
                    if not event.fail_quiet:
                        self.log("Unknown client!", event.uuid, lvl=critical)
                        self.log("Clients:", self._clients, lvl=debug)
                    return

                sock = self._clients[event.uuid].sock
                if not event.raw:
                    self.fireEvent(write(sock, jsonpacket), "wsserver")
                else:
                    self.log("Sending raw data to client", lvl=network)
                    self.fireEvent(write(sock, event.packet[:20]), "wsserver")

        except Exception as e:
            self.log("Exception during sending: %s (%s)" % (e, type(e)),
                     lvl=critical, exc=True)

    def broadcast(self, event):
        """Broadcasts an event either to all users or clients, depending on
        event flag"""
        try:
            if event.broadcasttype == "users":
                if len(self._users) > 0:
                    self.log("Broadcasting to all users:",
                             event.content, lvl=network)
                    for useruuid in self._users.keys():
                        self.fireEvent(
                            send(useruuid, event.content, sendtype="user"))
                        # else:
                        #    self.log("Not broadcasting, no users connected.",
                        #            lvl=debug)

            elif event.broadcasttype == "clients":
                if len(self._clients) > 0:
                    self.log("Broadcasting to all clients: ",
                             event.content, lvl=network)
                    for client in self._clients.values():
                        self.fireEvent(write(client.sock, event.content),
                                       "wsserver")
                        # else:
                        #    self.log("Not broadcasting, no clients
                        # connected.",
                        #            lvl=debug)
            elif event.broadcasttype == "socks":
                if len(self._sockets) > 0:
                    self.log("Emergency?! Broadcasting to all sockets: ",
                             event.content)
                    for sock in self._sockets:
                        self.fireEvent(write(sock, event.content), "wsserver")
                        # else:
                        #    self.log("Not broadcasting, no sockets
                        # connected.",
                        #            lvl=debug)

        except Exception as e:
            self.log("Error during broadcast: ", e, type(e), lvl=critical)

    def _checkPermissions(self, user, event):
        """Checks if the user has in any role that allows to fire the event."""

        for role in user.account.roles:
            if role in event.roles:
                self.log('Access granted', lvl=verbose)
                return True

        self.log('Access denied', lvl=verbose)
        return False

    def _handleAuthorizedEvents(self, component, action, data, user, client):
        """Isolated communication link for authorized events."""

        try:
            if component == "debugger":
                self.log(component, action, data, user, client, lvl=info)

            if not user and component in self.authorized_events.keys():
                self.log("Unknown client tried to do an authenticated "
                         "operation: %s",
                         component, action, data, user)
                return

            event = self.authorized_events[component][action]['event']

            self.log('Authorized event roles:', event.roles, lvl=hilight)
            if not self._checkPermissions(user, event):
                result = {
                    'component': 'hfos.ui.clientmanager',
                    'action': 'Permission',
                    'data': 'You have no role that allows this action.'
                }
                self.fireEvent(send(event.uuid, result))
                return

            self.log("Firing authorized event: ", component, action,
                     str(data)[:100], lvl=debug)
            # self.log("", (user, action, data, client), lvl=critical)
            self.fireEvent(event(user, action, data, client))
        except Exception as e:
            self.log("Critical error during authorized event handling:",
                     component, action, e,
                     type(e), lvl=critical, exc=True)

    def _handleAnonymousEvents(self, component, action, data, client):
        """Handler for anonymous (public) events"""
        try:
            event = self.anonymous_events[component][action]['event']

            self.log("Firing anonymous event: ", component, action,
                     str(data)[:20], lvl=network)
            # self.log("", (user, action, data, client), lvl=critical)
            self.fireEvent(event(action, data, client))
        except Exception as e:
            self.log("Critical error during anonymous event handling:",
                     component, action, e,
                     type(e), lvl=critical, exc=True)

    def _handleAuthenticationEvents(self, requestdata, requestaction,
                                    clientuuid, sock):
        """Handler for authentication events"""

        # TODO: Move this stuff over to ./auth.py
        if requestaction in ("login", "autologin"):
            try:
                self.log("Login request", lvl=verbose)

                if requestaction == "autologin":
                    username = password = None
                    requestedclientuuid = requestdata
                    auto = True

                    self.log("Autologin for", requestedclientuuid, lvl=debug)
                else:
                    username = requestdata['username']
                    password = requestdata['password']

                    if 'clientuuid' in requestdata:
                        requestedclientuuid = requestdata['clientuuid']
                    else:
                        requestedclientuuid = None
                    auto = False

                    self.log("Auth request by", username, lvl=verbose)

                self.fireEvent(authenticationrequest(
                    username,
                    password,
                    clientuuid,
                    requestedclientuuid,
                    sock,
                    auto,
                ), "auth")
                return
            except Exception as e:
                self.log("Login failed: ", e, type(e), lvl=warn, exc=True)
        elif requestaction == "logout":
            self.log("User logged out, refreshing client.", lvl=network)
            try:
                if clientuuid in self._clients:
                    client = self._clients[clientuuid]
                    user_id = client.useruuid
                    if client.useruuid:
                        self.log("Logout client uuid: ", clientuuid)
                        self._logoutclient(client.useruuid, clientuuid)
                    self.fireEvent(clientdisconnect(clientuuid))
                else:
                    self.log("Client is not connected!", lvl=warn)
            except Exception as e:
                self.log("Error during client logout: ", e, type(e),
                         lvl=error, exc=True)
        else:
            self.log("Unsupported auth action requested:",
                     requestaction, lvl=warn)

    @handler('reset_flood_counters')
    def _reset_flood_counters(self, *args):
        """Resets the flood counters on event trigger"""

        # self.log('Resetting flood counter')
        self._flood_counter = {}

    @handler('reset_flood_offenders')
    def _reset_flood_offenders(self, *args):
        """Resets the list of flood offenders on event trigger"""

        offenders = []
        # self.log('Resetting flood offenders')

        for offender, offence_time in self._flooding.items():
            if time() - offence_time < 10:
                self.log('Removed offender from flood list:', offender)
                offenders.append(offender)

        for offender in offenders:
            del self._flooding[offender]

    def _check_flood_protection(self, component, action, clientuuid):
        """Checks if any clients have been flooding the node"""

        if clientuuid not in self._flood_counter:
            self._flood_counter[clientuuid] = 0

        self._flood_counter[clientuuid] += 1

        if self._flood_counter[clientuuid] > 100:
            packet = {
                'component': 'hfos.ui.clientmanager',
                'action': 'Flooding',
                'data': True
            }
            self.fireEvent(send(clientuuid, packet))
            self.log('Flooding from', clientuuid)
            return True

    @handler("read", channel="wsserver")
    def read(self, *args):
        """Handles raw client requests and distributes them to the
        appropriate components"""

        self.log("Beginning new transaction: ", args, lvl=network)
        try:
            sock, msg = args[0], args[1]
            user = password = client = clientuuid = useruuid = requestdata = \
                requestaction = None
            # self.log("", msg)

            clientuuid = self._sockets[sock].clientuuid
        except Exception as e:
            self.log("Receiving error: ", e, type(e), lvl=error)

        if clientuuid in self._flooding:
            return

        try:
            msg = json.loads(msg)
            self.log("Message from client received: ", msg, lvl=network)
        except Exception as e:
            self.log("JSON Decoding failed! %s (%s of %s)" % (msg, e, type(e)))
            return

        try:
            requestcomponent = msg['component']
            requestaction = msg['action']
        except (KeyError, AttributeError) as e:
            self.log("Unpacking error: ", msg, e, type(e), lvl=error)
            return

        if self._check_flood_protection(requestcomponent, requestaction,
                                        clientuuid):
            self.log('Flood protection triggered')
            self._flooding[clientuuid] = time()

        try:
            # TODO: Do not unpickle or decode anything from unsafe events
            requestdata = msg['data']
            if isinstance(requestdata, (dict, list)) and 'raw' in requestdata:
                # self.log(requestdata['raw'], lvl=critical)
                requestdata['raw'] = b64decode(requestdata['raw'])
                # self.log(requestdata['raw'])
        except (KeyError, AttributeError) as e:
            self.log("No payload.", lvl=network)
            requestdata = None

        if requestcomponent == "auth":
            self._handleAuthenticationEvents(requestdata, requestaction,
                                             clientuuid, sock)
            return

        try:
            client = self._clients[clientuuid]
        except KeyError as e:
            self.log('Could not get client for request!', e, type(e), lvl=warn)
            return

        if requestcomponent in self.anonymous_events and requestaction in \
                self.anonymous_events[requestcomponent]:
            self.log('Executing anonymous event:', requestcomponent,
                     requestaction)
            try:
                self._handleAnonymousEvents(requestcomponent, requestaction,
                                            requestdata, client)
            except Exception as e:
                self.log("Anonymous request failed:", e, type(e), lvl=warn,
                         exc=True)
            return

        elif requestcomponent in self.authorized_events:
            try:
                useruuid = client.useruuid
                self.log("Authenticated operation requested by ",
                         client.config, lvl=network)
            except Exception as e:
                self.log("No useruuid!", e, type(e), lvl=critical)
                return

            try:
                user = self._users[useruuid]
            except KeyError:
                if not requestaction == 'ping' and requestcomponent == 'hfos.ui.clientmanager':
                    self.log("User not logged in.", lvl=warn)
                return

            try:
                self._handleAuthorizedEvents(requestcomponent, requestaction,
                                             requestdata, user, client)
            except Exception as e:
                self.log("User request failed: ", e, type(e), lvl=warn,
                         exc=True)
        else:
            self.log('Invalid event received:', requestcomponent, requestaction, lvl=warn)

    @handler("authentication", channel="auth")
    def authentication(self, event):
        """Links the client to the granted account and profile,
        then notifies the client"""

        try:
            self.log("Authorization has been granted by DB check:",
                     event.username, lvl=debug)

            account, profile, clientconfig = event.userdata

            useruuid = event.useruuid
            originatingclientuuid = event.clientuuid
            clientuuid = clientconfig.uuid

            if clientuuid != originatingclientuuid:
                self.log("Mutating client uuid to request id:",
                         clientuuid, lvl=network)
            # Assign client to user
            if useruuid in self._users:
                signedinuser = self._users[useruuid]
            else:
                signedinuser = User(account, profile, useruuid)
                self._users[account.uuid] = signedinuser

            if clientuuid in signedinuser.clients:
                self.log("Client configuration already logged in.",
                         lvl=critical)
                # TODO: What now??
                # Probably senseful would be to add the socket to the
                # client's other socket
                # The clients would be identical then - that could cause
                # problems
                # which could be remedied by duplicating the configuration
            else:
                signedinuser.clients.append(clientuuid)
                self.log("Active client (", clientuuid, ") registered to "
                                                        "user", useruuid,
                         lvl=debug)

            # Update socket..
            socket = self._sockets[event.sock]
            socket.clientuuid = clientuuid
            self._sockets[event.sock] = socket

            # ..and client lists
            # TODO: Rewrite and simplify this:
            newclient = Client(
                sock=event.sock,
                ip=socket.ip,
                clientuuid=clientuuid,
                useruuid=useruuid,
                name=clientconfig.name,
                config=clientconfig
            )

            del (self._clients[originatingclientuuid])
            self._clients[clientuuid] = newclient

            authpacket = {"component": "auth", "action": "login",
                          "data": account.serializablefields()}
            self.log("Transmitting Authorization to client", authpacket,
                     lvl=network)
            self.fireEvent(
                write(event.sock, json.dumps(authpacket)),
                "wsserver"
            )

            profilepacket = {"component": "profile", "action": "get",
                             "data": profile.serializablefields()}
            self.log("Transmitting Profile to client", profilepacket,
                     lvl=network)
            self.fireEvent(write(event.sock, json.dumps(profilepacket)),
                           "wsserver")

            clientconfigpacket = {"component": "clientconfig", "action": "get",
                                  "data": clientconfig.serializablefields()}
            self.log("Transmitting client configuration to client",
                     clientconfigpacket, lvl=network)
            self.fireEvent(write(event.sock, json.dumps(clientconfigpacket)),
                           "wsserver")

            self.fireEvent(userlogin(clientuuid, useruuid, clientconfig, signedinuser))

            self.log("User configured: Name",
                     signedinuser.account.name, "Profile",
                     signedinuser.profile.uuid, "Clients",
                     signedinuser.clients,
                     lvl=debug)

        except Exception as e:
            self.log("Error (%s, %s) during auth grant: %s" % (
                type(e), e, event), lvl=error)

    @handler(ping)
    def ping(self, event):
        self.log('Client ping received:', event.data)
        response = {
            'component': 'hfos.ui.clientmanager',
            'action': 'pong',
            'data': [event.data, time() * 1000]
        }

        self.fire(send(event.client.uuid, response))

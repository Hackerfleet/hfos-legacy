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


Module clientmanager
====================

Coordinates clients communicating via websocket


"""

import datetime
import json
from pprint import pprint

import random
from uuid import uuid4
from base64 import b64decode

from hfos.component import handler
from circuits.net.events import write
from hfos.events.system import get_user_events
from hfos.events.client import authenticationrequest, send, clientdisconnect, \
    userlogin
from hfos.component import ConfigurableComponent
from hfos.database import objectmodels
from hfos.logger import error, warn, critical, debug, info, network, \
    verbose, hilight
from hfos.ui.clientobjects import Socket, Client, User


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.time):
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
        self.log("Cleaning up client of logged in user.")
        try:
            self._users[useruuid].clients.remove(clientuuid)
            if len(self._users[useruuid].clients) == 0:
                self.log("Last client of user disconnected.")
                del self._users[useruuid]
            self._clients[clientuuid].useruuid = None
        except Exception as e:
            self.log("Error during client logout: ", e, type(e),
                     clientuuid, useruuid, lvl=error,
                     exc=True)

    @handler("connect", channel="wsserver")
    def connect(self, *args):
        """Registers new sockets and their clients and allocates uuids"""

        self.log("Connect ", args, lvl=debug)

        try:
            sock = args[0]
            ip = args[1]

            if sock not in self._sockets:
                self.log("New ip!", ip, lvl=debug)
                clientuuid = str(uuid4())
                self._sockets[sock] = Socket(ip, clientuuid)
                # Key uuid is temporary, until signin, will then be replaced
                #  with account uuid

                self._clients[clientuuid] = Client(
                    sock=sock,
                    ip=ip,
                    clientuuid=clientuuid,
                )

                self.log("Client connected:", clientuuid)
            else:
                self.log("Strange! Old IP reconnected!" + "#" * 15)
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

    def _handleAuthorizedEvents(self, component, action, data, user, client):
        """Isolated communication link for authorized events."""

        try:
            if component == "debugger":
                self.log(component, action, data, user, client, lvl=info)
            AuthorizedEvents = get_user_events()
            # pprint(AuthorizedEvents)

            if not user and component in AuthorizedEvents.keys():
                self.log("Unknown client tried to do an authenticated "
                         "operation: %s",
                         component, action, data, user)
                return

            event = AuthorizedEvents[component][action]['event']

            self.log("Firing authorized event: ", component, action,
                     str(data)[:20], lvl=network)
            # self.log("", (user, action, data, client), lvl=critical)
            self.fireEvent(event(user, action, data, client))
        except Exception as e:
            self.log("Critical error during authorized event handling:", e,
                     type(e), lvl=critical, exc=True)

    def _handleAuthenticationEvents(self, requestdata, requestaction,
                                    clientuuid, sock):
        # TODO: Move this stuff over to ./auth.py
        if requestaction in ("login", "autologin"):
            try:
                self.log("Login request")

                if requestaction == "autologin":
                    username = password = None
                    requestedclientuuid = requestdata
                    auto = True

                    self.log("Autologin for", requestedclientuuid)
                else:
                    username = requestdata['username']
                    password = requestdata['password']

                    if 'clientuuid' in requestdata:
                        requestedclientuuid = requestdata['clientuuid']
                    else:
                        requestedclientuuid = None
                    auto = False

                    self.log("Auth request by", username)

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
                    if client.useruuid:
                        self.log("Logout client uuid: ", clientuuid)
                        self._logoutclient(client.useruuid, clientuuid)
                    self.fireEvent(clientdisconnect(clientuuid))
                else:
                    self.log("Client is not connected!", lvl=warn)
            except Exception as e:
                self.log("Error during client logout: ", e, type(e),
                         lvl=error)
        else:
            self.log("Unsupported auth action requested:",
                     requestaction, lvl=warn)

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

        try:
            requestdata = msg['data']
            if 'raw' in requestdata:
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
            # Only for signed in users
            client = self._clients[clientuuid]
            useruuid = client.useruuid
            self.log("Authenticated operation requested by ",
                     client.config, lvl=network)
        except Exception as e:
            self.log("No useruuid!", e, type(e), lvl=critical)
            return

        try:
            user = self._users[useruuid]
        except KeyError:
            self.log("User not logged in.", lvl=warn)
            return

        try:
            self._handleAuthorizedEvents(requestcomponent, requestaction,
                                         requestdata, user, client)
        except Exception as e:
            self.log("Requested action failed: ", e, lvl=warn)

    @handler("authentication", channel="auth")
    def authentication(self, event):
        """Links the client to the granted account and profile,
        then notifies the client"""
        try:
            self.log("Authorization has been granted by DB check:",
                     event.username)

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
                         lvl=info)

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

            self.fireEvent(userlogin(clientuuid, useruuid))

            self.log("User configured: Name",
                     signedinuser.account.name, "Profile",
                     signedinuser.profile.uuid, "Clients",
                     signedinuser.clients,
                     lvl=info)

        except Exception as e:
            self.log("Error (%s, %s) during auth grant: %s" % (
                type(e), e, event), lvl=error)

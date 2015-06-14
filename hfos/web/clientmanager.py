"""


Module clientmanager
====================

Coordinates clients communicating via websocket

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

import json
from uuid import uuid4

from circuits.net.events import write
from circuits import Component, handler

from hfos.events import send, authenticationrequest, clientdisconnect, AuthorizedEvents
from hfos.logger import hfoslog, error, warn, critical, debug, info, verbose


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

    def __init__(self, sock, ip, clientuuid, useruuid=None, name=''):
        """

        :param sock: Associated connection
        :param ip: Associated Internet protocol address
        :param clientuuid: Unique Uniform ID of this client
        """
        super(Client, self).__init__()
        self.sock = sock
        self.ip = ip
        self.clientuuid = clientuuid
        self.useruuid = useruuid
        if name == '':
            self.name = clientuuid
        else:
            self.name = name


class User(object):
    """
    Authenticated clients with profile etc
    """

    def __init__(self, account, profile, useruuid):
        """

        :param account: userobject
        :param profile: profileobject
        :param useruuid: profileobject
        :param clients: List of clients' UUIDs
        :param args:
        """
        super(User, self).__init__()
        self.clients = []
        self.useruuid = useruuid
        self.profile = profile
        self.account = account


class ClientManager(Component):
    """
    Handles client connections and requests as well as client-outbound communication.
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(ClientManager, self).__init__(*args)

        self._clients = {}
        self._sockets = {}
        self._users = {}
        self._count = 0

    @handler("disconnect", channel="wsserver")
    def disconnect(self, sock):
        """Handles socket disconnections"""

        hfoslog("[CM] Disconnect ", sock)

        if sock in self._sockets:
            hfoslog("[CM] Deleting socket")
            sockobj = self._sockets[sock]
            clientuuid = sockobj.clientuuid

            self.fireEvent(clientdisconnect(clientuuid, self._clients[clientuuid].useruuid))

            del self._sockets[sock]
            del self._clients[clientuuid]

    @handler("connect", channel="wsserver")
    def connect(self, *args):
        """Registers new sockets and their clients and allocates uuids"""

        hfoslog("[CM] Connect ", args)
        sock = args[0]
        ip = args[1]

        if sock not in self._sockets:
            hfoslog("[CM] New ip!", ip)
            clientuuid = str(uuid4())
            self._sockets[sock] = Socket(ip, clientuuid)
            # Key uuid is temporary, until signin, will then be replaced with account uuid
            self._clients[clientuuid] = Client(sock, ip, clientuuid)
            self.fireEvent(write(sock, json.dumps({'type': 'info', 'content': 'Connected'})))
            hfoslog("[CM] Client connected:", clientuuid)
        else:
            hfoslog("[CM] Strange! Old IP reconnected!" + "#" * 15)
            #     self.fireEvent(write(sock, "Another client is connecting from your IP!"))
            #     self._sockets[sock] = (ip, uuid.uuid4())

    def send(self, event):
        """Sends a packet to an already known user or one of his clients by UUID"""

        try:
            if event.sendtype == "user":
                hfoslog("[CM] Broadcasting to all of users clients: '%s': '%s" % (event.uuid, event.packet))
                if event.uuid not in self._users:
                    hfoslog('[CM] Unknown user! ', event, lvl=critical)
                    return
                clients = self._users[event.uuid].clients

                for clientuuid in clients:
                    sock = self._clients[clientuuid].sock

                    if not event.raw:
                        self.fireEvent(write(sock, json.dumps(event.packet)), "wsserver")
                    else:
                        hfoslog("[CM] Sending raw data to client")
                        self.fireEvent(write(sock, event.packet), "wsserver")
            else:  # only to client
                hfoslog("[CM] Sending to user's client: '%s': '%.50s ..." % (event.uuid, event.packet), lvl=debug)
                if event.uuid not in self._clients:
                    hfoslog('[CM] Unknown client! ', event.uuid, lvl=critical)
                    hfoslog('[CM] Clients: ', self._clients, lvl=debug)
                    return

                sock = self._clients[event.uuid].sock
                if not event.raw:
                    self.fireEvent(write(sock, json.dumps(event.packet)), "wsserver")
                else:
                    hfoslog("[CM] Sending raw data to client")
                    self.fireEvent(write(sock, event.packet), "wsserver")

        except Exception as e:
            hfoslog("[CM] Exception during sending: %.50s (%s)" % (e, type(e)))

    def broadcast(self, event):
        """Broadcasts an event either to all users or clients, depending on event flag"""
        try:
            if event.broadcasttype == "users":
                hfoslog("[CM] Broadcasting to all users:", event.content)
                for useruuid in self._users.keys():
                    self.fireEvent(send(useruuid, event.content, sendtype="user"))

            elif event.broadcasttype == "clients":
                hfoslog("[CM] Broadcasting to all clients: ", event.content)
                for client in self._clients.values():
                    self.fireEvent(write(client.sock, event.content), "wsserver")

            elif event.broadcasttype == "socks":
                hfoslog("[CM] Emergency?! Broadcasting to all sockets: ", event.content)
                for sock in self._sockets:
                    self.fireEvent(write(sock, event.content), "wsserver")

        except Exception as e:
            hfoslog("[CM] Error during broadcast: ", e, type(e), lvl=critical)

    def _handleAuthorizedEvents(self, component, action, data, user, client):
        try:
            if component == "debugger":
                hfoslog('[CM]', component, action, data, user, client, lvl=critical)
            if not user and component in AuthorizedEvents.keys():
                hfoslog("[CM] Unknown client tried to do an authenticated operation: %s", component, action, data, user)
                return

            event = AuthorizedEvents[component]
            # hfoslog(event, lvl=critical)
            hfoslog("[CM] Firing authorized event.", lvl=debug)
            # hfoslog("[CM] ", (user, action, data, client), lvl=critical)
            self.fireEvent(event(user, action, data, client))
        except Exception as e:
            hfoslog("[CM] Critical error during authorized event handling:", e, type(e), lvl=critical)

    def _handleAuthenticationEvents(self, requestdata, requestaction, clientuuid, sock):
        if requestaction == "login":
            try:
                hfoslog("[CM] Login request")

                username = requestdata['username']
                password = requestdata['password']
                newclientuuid = requestdata['clientuuid']
                hfoslog("[CM] Auth request by ", username)

                self.fireEvent(authenticationrequest(username, password, clientuuid, newclientuuid, sock), "auth")
                return
            except Exception as e:
                hfoslog("[CM] Login failed: ", e, lvl=warn)
        elif requestaction == "logout":
            hfoslog("[CM] User logged out, refreshing client.")
            self.fireEvent(clientdisconnect(clientuuid))


    @handler("read", channel="wsserver")
    def read(self, *args):
        """Handles raw client requests and distributes them to the appropriate components"""
        try:
            sock, msg = args[0], args[1]
            user = password = client = clientuuid = useruuid = requestdata = requestaction = None
            # hfoslog("[CM] ", msg)

            clientuuid = self._sockets[sock].clientuuid
        except Exception as e:
            hfoslog("[CM] Receiving error: ", e, type(e),)

        try:
            msg = json.loads(msg)
        except Exception as e:
            hfoslog("[CM] JSON Decoding failed! %s (%s of %s)" % (msg, e, type(e)))
            return

        try:
            requestcomponent = msg['message']['component']
            requestaction = msg['message']['action']
        except (KeyError, AttributeError) as e:
            hfoslog("[CM] Unpacking error: ", msg, e, type(e), lvl=error)
            return

        try:
            requestdata = msg['message']['data']
        except (KeyError, AttributeError) as e:
            hfoslog("[CM] No payload.", lvl=verbose)
            requestdata = None

        if requestcomponent == "auth":
            self._handleAuthenticationEvents(requestdata, requestaction, clientuuid, sock)

        try:
            # Only for signed in users
            client = self._clients[clientuuid]
            useruuid = client.useruuid
            hfoslog("[CM] Authenticated operation requested by ", client, lvl=debug)
        except Exception as e:
            hfoslog("[CM] No useruuid!", lvl=critical)
            return
        if requestcomponent == "auth":
            if requestaction == "logout":
                hfoslog("[CM] Client logged out:")
                self._users[useruuid].clients.remove(clientuuid)
                self._clients[clientuuid].useruuid = None
            return

        try:
            user = self._users[useruuid]
        except KeyError:
            hfoslog("[CM] User not logged in.", lvl=warn)
            return

        try:
            self._handleAuthorizedEvents(requestcomponent, requestaction, requestdata, user, client)
        except Exception as e:
            hfoslog("[CM] Requested action failed: ", e, lvl=warn)

    @handler("authentication", channel="auth")
    def authentication(self, event):
        """Links the client to the granted account and profile, then notifies the client"""
        try:
            hfoslog("[CM] Authorization has been granted by DB check: %s" % event)

            account, profile = event.userdata

            clientuuid = event.clientuuid
            useruuid = event.useruuid

            signedinuser = User(account, profile, useruuid)
            signedinuser.clients.append(clientuuid)
            self._users[account.uuid] = signedinuser

            self._clients[clientuuid].useruuid = useruuid

            authpacket = {"component": "auth", "action": "login", "data": account.serializablefields()}
            hfoslog("[CM] Transmitting Authorization to client", authpacket, lvl=debug)
            self.fireEvent(write(event.sock, json.dumps(authpacket)), "wsserver")

            if profile:
                profilepacket = {"component": "profile", "action": "get", "data": profile.serializablefields()}
                hfoslog("[CM] Transmitting Profile to client", profilepacket, lvl=debug)
                self.fireEvent(write(event.sock, json.dumps(profilepacket)), "wsserver")

            hfoslog("[CM] User configured:", signedinuser.__dict__, lvl=info)

        except Exception as e:
            hfoslog("[CM] Error (%s, %s) during auth grant: %s" % (type(e), e, event), lvl=error)

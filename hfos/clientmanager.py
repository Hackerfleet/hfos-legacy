"""
Hackerfleet Operating System - Backend

Module clientmanager
====================

Coordinates clients communicating via websocket

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

import json
from uuid import uuid4
from time import time

from circuits.net.events import write
from circuits import Component, handler

from hfos.events import authenticationrequest, profileupdate, chatevent, chatmessage, mapviewrequest, send
from hfos.logger import hfoslog, error, warn


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

    def __init__(self, sock, ip, clientuuid, useruuid=None):
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
    channel = "wsserver"

    def __init__(self, *args):
        super(ClientManager, self).__init__(*args)

        self._clients = {}
        self._sockets = {}
        self._users = {}
        self._count = 0

    def disconnect(self, sock):
        """Handles socket disconnections"""

        hfoslog("CA: Disconnect ", sock)

        if sock in self._sockets:
            hfoslog("CA: Deleting socket")
            # TODO: Delete client as well
            del self._sockets[sock]

    def connect(self, *args):
        """Registers new sockets and their clients and allocates uuids"""

        hfoslog("CA: Connect ", args)
        sock = args[0]
        ip = args[1]

        if sock not in self._sockets:
            hfoslog("CA: New ip!", ip)
            clientuuid = str(uuid4())
            self._sockets[sock] = Socket(ip, clientuuid)
            # Key uuid is temporary, until signin, will then be replaced with account uuid
            self._clients[clientuuid] = Client(sock, ip, clientuuid)
            self.fireEvent(write(sock, json.dumps({'type': 'info', 'content': 'Connected'})))
            hfoslog("Client connected:", clientuuid)
        else:
            hfoslog("CA: Strange! Old IP reconnected!" + "#" * 15)
            #     self.fireEvent(write(sock, "Another client is connecting from your IP!"))
            #     self._sockets[sock] = (ip, uuid.uuid4())

    @handler("send")
    def send(self, event):
        """Sends a packet to an already known client by UUID"""

        hfoslog("CM: Sending to client '%s': '%s" % (event.uuid, event.packet))
        try:
            hfoslog(self._users[event.uuid])
            clients = self._users[event.uuid].clients

            for clientuuid in clients:
                sock = self._clients[clientuuid].sock
                self.fireEvent(write(sock, json.dumps(event.packet)))
        except Exception as e:
            hfoslog("CM: Exception during sending: %s (%s)" % (e, type(e)))

    @handler("broadcast")
    def broadcast(self, event):
        """Broadcasts an event either to all users or clients, depending on event flag"""

        if event.type == "users":
            hfoslog("CM: Broadcasting to all users:", event.content)
            for user in self._users:
                self.fireEvent(send(user.useruuid, event.content))
        elif event.type == "clients":
            hfoslog("CM: Broadcasting to all clients: ", event.content)
            for client in self._clients:
                self.fireEvent(write(client.sock, event.content))
        elif event.type == "socks":
            hfoslog("CM: Emergency?! Broadcasting to all sockets: ", event.content)
            for sock in self._sockets:
                self.fireEvent(write(sock, event.content))

    def read(self, *args):
        """Handles raw client requests and distributes them to the appropriate components"""
        timestamp = time()

        sock, msg = args[0], args[1]
        hfoslog("CM: ", msg)

        clientuuid = self._sockets[sock].clientuuid
        # TODO: Make a difference between coonnection and user uuid
        try:
            msg = json.loads(msg)
        except Exception as e:
            hfoslog("CM: JSON Decoding failed! %s (%s of %s)" % (msg, e, type(e)))

        try:
            if "message" in msg.keys():
                msg = msg['message']
                if "type" in msg.keys():
                    msgtype = msg['type']
                    if msgtype == "info":
                        # uuuh.
                        return

                    if msgtype == "auth":
                        auth = msg['content']
                        username = auth['username']
                        hfoslog("CM: Auth request by ", username)

                        self.fireEvent(authenticationrequest(auth['username'], auth['password'], clientuuid, sock),
                                       "auth")
                        return

                    try:
                        # Only for signed in users
                        client = self._clients[clientuuid]
                        useruuid = client.useruuid
                        hfoslog("CM: Authenticated operation tried by ", client)
                    except Exception as e:
                        hfoslog("No useruuid.", lvl=warn)
                        return

                    try:
                        userobj = self._users[useruuid]
                    except KeyError:
                        hfoslog("User not logged in.", lvl=warn)
                        return

                    if not useruuid and msgtype in ("profile", "mapview", "chat"):
                        hfoslog("CM: Unknown client tried to do an authenticated operation: %s" % msg)
                        return

                    if msgtype == "profile":
                        profile = msg['content']
                        hfoslog("CM: Profile update")

                        self.fireEvent(profileupdate(profile, useruuid, sock), "auth")
                        return

                    if msgtype == "mapview":
                        details = msg['content']
                        hfoslog("CM: Mapview request")

                        self.fireEvent(mapviewrequest(userobj, details), "mapview")
                        return

                    if msgtype == "chatrequest":
                        chatdata = msg['content']
                        hfoslog("CM: Chat request '%s'" % chatdata)

                        useraccount = self._users[useruuid]

                        self.fireEvent(chatevent(useraccount, timestamp, chatdata), "chat")
                        return

        except Exception as e:
            hfoslog("CM: Erroneous (%s, %s) message received: %s" % (type(e), e, msg))

    @handler("authentication")
    def on_authgranted(self, event):
        """Links the client to the granted account and profile, then notifies the client"""
        try:
            hfoslog("CM: Authorization has been granted by DB check: %s" % event)

            account, profile = event.userdata

            clientuuid = event.clientuuid
            useruuid = event.useruuid

            signedinuser = User(account, profile, useruuid)
            signedinuser.clients.append(clientuuid)
            self._users[account.uuid] = signedinuser

            self._clients[clientuuid].useruuid = useruuid

            authpacket = {"type": "auth", "content": {"success": True, "useraccount": account.serializablefields()}}
            self.fireEvent(write(event.sock, json.dumps(authpacket)))

            profilepacket = {"type": "profile", "content": profile.serializablefields()}
            self.fireEvent(write(event.sock, json.dumps(profilepacket)))

            self.fireEvent(event, "chat")
            hfoslog("User configured:", signedinuser.__dict__)

        except Exception as e:
            hfoslog("CM: Error (%s, %s) during auth grant: %s" % (type(e), e, event))

    @handler("ping")
    def on_ping(self, *args, **kwargs):
        """Pings all connected clients with stupid ping/demo messages"""
        self._count += 1
        hfoslog("CA: Ping %i" % self._count)
        for sock in self._sockets:
            ip = self._sockets[sock].ip
            hfoslog("CA: Sending ping to %s " % ip)
            data = {'type': 'info',
                    'content': "Hello " + str(self._sockets[sock].clientuuid)
            }
            if (self._count % 5) == 0:
                data = {'type': 'navdata',
                        'content': {'true_course': 17,
                                    'spd_over_grnd': 23
                        }
                }
            self.fireEvent(write(sock, json.dumps(data)))


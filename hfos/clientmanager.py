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

from .events import authenticationrequest, profileupdate, chatevent, chatmessage, mapviewupdaterequest


class Client(object):
    """
    Client metadata object
    """

    def __init__(self, sock, ip, uuid, profile=None, account=None):
        """

        :param sock: Associated connection
        :param ip: Associated Internet protocol address
        :param uuid: Unique Uniform ID of connection
        :param profile: User profile object
        :param account: User account object
        """
        super(Client, self).__init__()
        self.sock = sock
        self.ip = ip
        self.uuid = uuid
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
        self._count = 0

    def disconnect(self, sock):
        """Handles socket disconnections"""

        print("CA: Disconnect ", sock)

        if sock in self._sockets:
            print("CA: Deleting socket")
            # TODO: Delete client as well
            del self._sockets[sock]

    def connect(self, *args):
        """Registers new sockets and their clients and allocates uuids"""

        print("CA: Connect ", args)
        sock = args[0]
        ip = args[1]

        if sock not in self._sockets:
            print("CA: New ip!", ip)
            uuid = uuid4()
            self._sockets[sock] = (ip, uuid)
            self._clients[uuid] = Client(sock, ip, uuid)
            self.fireEvent(write(sock, json.dumps({'type': 'info', 'content': 'Connected'})))
        else:
            print("CA: Strange! Old IP reconnected!" + "#" * 15)
            #     self.fireEvent(write(sock, "Another client is connecting from your IP!"))
            #     self._sockets[sock] = (ip, uuid.uuid4())

    def send(self, *args):
        """Sends a packet to an already known client by UUID"""

        uuid, packet = args[0], args[1]
        print("CM: Sending to client '%s': '%s" % (uuid, packet))
        try:
            sock = self._clients[uuid].sock
            self.fireEvent(write(sock, json.dumps(packet)))
        except Exception as e:
            print("CM: Exception during sending: %s (%s)" % (e, type(e)))

    def read(self, *args):
        """Handles raw client requests and distributes them to the appropriate components"""

        sock, msg = args[0], args[1]
        print("CM: ", msg)

        useruuid = self._sockets[sock][1]

        try:
            msg = json.loads(msg)
        except Exception as e:
            print("CM: JSON Decoding failed! %s (%s of %s)" % (msg, e, type(e)))

        try:
            if "message" in msg.keys():
                msg = msg['message']
                if "type" in msg.keys():
                    msgtype = msg['type']
                    if msgtype == "auth":
                        auth = msg['content']
                        print("CM: Authrequest")

                        self.fireEvent(authenticationrequest(auth['username'], auth['password'], useruuid, sock),
                                       "auth")

                    if msgtype == "profile":
                        profile = msg['content']
                        print("CM: Profileupdate")

                        self.fireEvent(profileupdate(profile, useruuid, sock), "auth")

                    if msgtype == "mapview":
                        mapview = msg['content']
                        print("CM: Mapview request")

                        self.fireEvent(mapviewupdaterequest(useruuid, mapview), "mapview")

                    if msgtype in ("chatevent", "chatmessage"):
                        chatdata = msg['content']
                        timestamp = time()

                        print("CM: Chatrequest '%s'" % chatdata)

                        event = None

                        if msgtype == "chatmessage":
                            event = chatmessage(sender=self._clients[useruuid], msg=chatdata, timestamp=timestamp)
                        elif msgtype == "chatevent":
                            event = chatevent(sender=self._clients[useruuid], msgtype=chatdata, timestamp=timestamp)
                        if event:
                            self.fireEvent(event, "chat")

        except Exception as e:
            print("CM: Erroneous (%s, %s) message received: %s" % (type(e), e, msg))

    @handler("authentication")
    def on_authgranted(self, event):
        """Links the client to the granted account and profile, then notifies the client"""
        try:
            print("CM: Authorization has been granted by DB check: %s" % event)

            account, profile = event.userdata

            self._clients[event.uuid].profile = profile
            self._clients[event.uuid].account = account

            authpacket = {"type": "auth", "content": {"success": True, "useraccount": account.serializablefields()}}
            self.fireEvent(write(event.sock, json.dumps(authpacket)))

            profilepacket = {"type": "profile", "content": profile.serializablefields()}
            self.fireEvent(write(event.sock, json.dumps(profilepacket)))

        except Exception as e:
            print("CM: Error (%s, %s) during auth grant: %s" % (type(e), e, event))

    @handler("ping")
    def on_ping(self, *args, **kwargs):
        """Pings all connected clients with stupid ping/demo messages"""
        self._count += 1
        print("CA: Ping %i" % self._count)
        for sock in self._sockets:
            ip = self._sockets[sock][0]
            print("CA: Sending ping to %s " % ip)
            data = {'type': 'info',
                    'content': "Hello " + str(self._sockets[sock][1])
            }
            if (self._count % 5) == 0:
                data = {'type': 'navdata',
                        'content': {'true_course': 17,
                                    'spd_over_grnd': 23
                        }
                }
            self.fireEvent(write(sock, json.dumps(data)))


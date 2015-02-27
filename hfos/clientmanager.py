from circuits.net.events import write, read
from circuits import Component, handler, Timer

from .auth import authrequest, authgranted

import json
from uuid import uuid4

from pprint import pprint

class ClientManager(Component):

    channel="wsserver"

    def init(self):
        self._clients = {}
        self._sockets = {}
        self._count = 0

    def disconnect(self, sock):
        print("CA: Disconnect ", sock)

        if sock in self._sockets:
            print("CA: Deleting socket")
            del self._sockets[sock]

    def connect(self, *args):
        print("CA: Connect ", args)
        sock = args[0]
        ip = args[1]
        print(sock, ip)
        if sock not in self._sockets:
            print("CA: New ip!", ip)
            uuid = uuid4()
            self._sockets[sock] = (ip, uuid)
            self._clients[uuid] = (sock, ip)
        else:
            print("CA: Strange! Old IP reconnected!" + "#"*15)
        #     self.fireEvent(write(sock, "Another client is connecting from your IP!"))
        #     self._sockets[sock] = (ip, uuid.uuid4())

    def read(self, *args):
        sock, msg = args[0], args[1]
        print("CM: ", msg)
        try:
            msg = json.loads(msg)
        except:
            print("CM: JSON Decoding failed! %s " % (msg))

        try:
            if "message" in msg.keys():
                msg = msg['message']
                if "type" in msg.keys():
                    if msg['type'] == "auth":
                        auth = msg['content']
                        print("CM: Authrequest!")
                        useruuid = self._sockets[sock][1]
                        self.fireEvent(authrequest(auth['username'], auth['password'], useruuid, sock))
        except Exception as e:
            print("CM: Erroneous (%s, %s) message received: %s" % (type(e), e, msg))

    @handler("authgranted")
    def on_authgranted(self, event):
        print("CM: Authorization has been granted by DB check: %s" % (event))

        print(str(event.useraccount))
        print(str(event.uuid))
        authpacket = {"type": "auth", "content": {"success": True, "profile": event.useraccount}}
        self.fireEvent(write(event.sock, json.dumps(authpacket)))


    @handler("ping")
    def on_ping(self, *args, **kwargs):
        self._count += 1
        print("CA: Ping %i" % (self._count))
        for sock in self._sockets:
            ip = self._sockets[sock][0]
            print("CA: Sending ping to %s " % ip)
            data = {'type': 'info',
                    'content':"Hello "+str(self._sockets[sock][1])
            }
            if (self._count % 5) == 0:
                data = {'type': 'navdata',
                        'content': {'true_course': 17,
                                    'spd_over_grnd': 23
                        }
                }
            self.fireEvent(write(sock, json.dumps(data)))


from circuits.net.events import write, read
from circuits import Component, handler, Timer

from .auth import authrequest, authgranted
from .chat import chatevent, chatmessage

import json
from uuid import uuid4
from time import time

from pprint import pprint

class Client(object):
    def __init__(self, sock, ip, uuid, profile=None):
        super(Client, self).__init__()
        self.sock = sock
        self.ip = ip
        self.uuid = uuid
        self.profile = profile


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

        if sock not in self._sockets:
            print("CA: New ip!", ip)
            uuid = uuid4()
            self._sockets[sock] = (ip, uuid)
            self._clients[uuid] = Client(sock, ip, uuid)
            self.fireEvent(write(sock, json.dumps({'type': 'info', 'content': 'Connected'})))
        else:
            print("CA: Strange! Old IP reconnected!" + "#"*15)
        #     self.fireEvent(write(sock, "Another client is connecting from your IP!"))
        #     self._sockets[sock] = (ip, uuid.uuid4())

    def read(self, *args):
        sock, msg = args[0], args[1]
        print("CM: ", msg)

        useruuid = self._sockets[sock][1]

        try:
            msg = json.loads(msg)
        except:
            print("CM: JSON Decoding failed! %s " % (msg))

        try:
            if "message" in msg.keys():
                msg = msg['message']
                if "type" in msg.keys():
                    msgtype = msg['type']
                    if msgtype == "auth":
                        auth = msg['content']
                        print("CM: Authrequest")
                        self.fireEvent(authrequest(auth['username'], auth['password'], useruuid, sock), "auth")
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

    @handler("authgranted")
    def on_authgranted(self, event):
        print("CM: Authorization has been granted by DB check: %s" % (event))
        self._clients[event.uuid].profile = event.useraccount
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


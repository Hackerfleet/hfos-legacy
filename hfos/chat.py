from circuits.net.events import write, read
from circuits import Component, handler, Event

from .auth import authrequest, authgranted

import json
from uuid import uuid4

from pprint import pprint




class chatmessage(Event):
    def __init__(self, msg, sender, timestamp, *args):
        super(chatmessage, self).__init__(*args)
        self.sender = sender
        self.timestamp = timestamp
        self.msg = msg

        print("CHAT: Message generated")

class chatevent(Event):
    def __init__(self, msgtype, sender, timestamp, *args):
        super(chatevent, self).__init__(*args)
        self.sender = sender
        self.timestamp = timestamp
        self.msgtype = msgtype

        print("CHAT: Event generated")

class Chat(Component):

    channel="chat"

    def init(self):
        print("CHAT: Started")
        self._clients = []

    def _broadcast(self, chatpacket):
        print("CHAT: Transmitting message '%s'" % chatpacket)
        for recipient in self._clients:
            self.fireEvent(write(recipient.sock, json.dumps(chatpacket)), "wsserver")


    @handler("chatevent")
    def on_chatevent(self, event):
        print("CHAT: Event: '%s'" % event.__dict__)
        try:
            msgtype = event.msgtype
            print(event.sender.profile)
            username = event.sender.profile['username']
            print(username)
            if msgtype == "join":
                self._clients.append(event.sender)
                msg = "joined"
            if msgtype == "part":
                msg = "left"
                if event.sender in self._clients:
                    self._clients.remove(event.sender)
            # TODO: Make this a representation of the event itself
            chatpacket = {'type': 'chat', 'content': {'sender': username, 'timestamp': event.timestamp, 'content': msg}}
            self._broadcast(chatpacket)
            
            if msgtype == "part" and event.sender in self._clients:
                self._clients.remove(event.sender)

        except Exception as e:
            print("CHAT: Error: '%s'" % e)



    @handler("chatmessage")
    def on_chatmessage(self, event):
        print("CHAT: Event: '%s'" % event.__dict__)
        try:
            # TODO: Make this a representation of the event itself
            chatpacket = {'type': 'chat', 'content': {'sender': event.sender.profile['username'], 'timestamp': event.timestamp, 'content': ":" + str(event.msg)}}
            self._broadcast(chatpacket)
        except Exception as e:
            print("CHAT: Error: '%s'" % e)
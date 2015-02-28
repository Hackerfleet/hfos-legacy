#!/usr/bin/env python

from circuits import Component, Debugger, Event, Timer
from circuits.web.websockets.dispatcher import WebSocketsDispatcher
from circuits.web import Logger, Server, Static

from hfos.tilecache import TileCache
from hfos.clientmanager import ClientManager
from hfos.clientechoer import ClientEchoer
from hfos.auth import Auth
from hfos.chat import Chat
from hfos.nmea import NMEAParser


import webbrowser


class App(Component):
    def __init__(self):
        super(App, self).__init__()
        print("Firing up HFOS")

    def started(self, component):
        print("App: Creating timer for CA")
        Timer(30, Event.create("ping", channels="wsserver"), persist=True).register(self)


server = Server(("0.0.0.0", 8055))
app = App().register(server)

TileCache().register(server)
Static("/", docroot="/var/lib/hfos/static" ).register(server)
WebSocketsDispatcher("/websocket").register(server)
clientmanager = ClientManager().register(server)
Auth().register(clientmanager)
Chat().register(clientmanager)

NMEAParser().register(app)

Debugger().register(server)
Logger().register(server)
#ClientEchoer().register(server)


#webbrowser.open("http://127.0.0.1:8055")

print("Running...")
server.run()
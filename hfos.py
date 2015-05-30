#!/usr/bin/env python

"""
Hackerfleet Operating System - Backend

Application
===========

See README.rst for Build/Installation and setup details.

URLs & Contact
==============

Hackerfleet Homepage: http://hackerfleet.org
Mail: info@hackerfleet.org
IRC: #hackerfleet@irc.freenode.org

Project repository: http://github.com/hackerfleet/hfos
Frontend repository: http://github.com/hackerfleet/hfos-frontend

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from circuits import Component, Debugger, Event, Timer
from circuits.web.websockets.dispatcher import WebSocketsDispatcher
from circuits.web import Logger, Server, Static
# from circuits.tools import graph

import hfos.database

from hfos.tilecache import TileCache
from hfos.machineroom import Machineroom
from hfos.remotecontrolmanager import RemoteControlManager
from hfos.clientmanager import ClientManager
from hfos.mapviewmanager import MapViewManager
from hfos.layermanager import LayerManager
from hfos.schemamanager import SchemaManager
from hfos.camera import CameraManager
from hfos.auth import Authenticator
from hfos.logger import hfoslog
from hfos.debugger import HFDebugger

from hfos.chat import Chat
from hfos.nmea import NMEAParser

import webbrowser

from hfos.machineroom import machine, pump, rudder


class App(Component):
    """HFOS Core Backend Application"""

    def __init__(self):
        super(App, self).__init__()
        hfoslog("Firing up HFOS")

    def started(self, component):
        """Sets up the not-yet-so-useful Ping timer for demo purposes"""
        hfoslog("App: Creating timer for CA")
        Timer(5, Event.create("ping"), channels='wsserver', persist=True).register(self)
        # Timer(5, rudder(20), channels='machineroom', persist=True).register(self)



server = Server(("0.0.0.0", 8055))

HFDebugger().register(server)

app = App().register(server)

Machineroom().register(app)
NMEAParser().register(app)

TileCache().register(server)
Static("/", docroot="/var/lib/hfos/static").register(server)
WebSocketsDispatcher("/websocket").register(server)

clientmanager = ClientManager().register(server)
SchemaManager().register(clientmanager)
Authenticator().register(clientmanager)
Chat().register(clientmanager)
MapViewManager().register(clientmanager)
RemoteControlManager().register(clientmanager)
#CameraManager().register(clientmanager)

#Logger().register(server)

dbg = Debugger()
# dbg.IgnoreEvents.extend(["write", "_write", "streamsuccess"])
dbg.register(server)


#webbrowser.open("http://127.0.0.1:8055")

hfoslog("Running...")
#graph(server)
server.run()
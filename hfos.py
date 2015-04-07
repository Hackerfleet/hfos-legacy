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

import hfos.database

from hfos.tilecache import TileCache
from hfos.clientmanager import ClientManager
from hfos.mapviewmanager import MapViewManager
from hfos.layermanager import LayerManager
from hfos.schemamanager import SchemaManager
from hfos.auth import Authenticator
from hfos.logger import hfoslog
from hfos.debugger import HFDebugger

from hfos.chat import Chat
from hfos.nmea import NMEAParser

import webbrowser


class App(Component):
    """HFOS Core Backend Application"""

    def __init__(self):
        super(App, self).__init__()
        hfoslog("Firing up HFOS")

    def started(self, component):
        """Sets up the not-yet-so-useful Ping timer for demo purposes"""
        hfoslog("App: Creating timer for CA")
        Timer(90, Event.create("ping", channels="wsserver"), persist=True).register(self)


server = Server(("0.0.0.0", 8055))

app = App().register(server)

HFDebugger().register(server)
TileCache().register(server)
Static("/", docroot="/var/lib/hfos/static").register(server)
WebSocketsDispatcher("/websocket").register(server)
clientmanager = ClientManager().register(server)
Authenticator().register(clientmanager)
Chat().register(clientmanager)
MapViewManager().register(clientmanager)
SchemaManager().register(clientmanager)
Logger().register(server)

NMEAParser().register(app)

Debugger().register(server)


#webbrowser.open("http://127.0.0.1:8055")

hfoslog("Running...")
server.run()
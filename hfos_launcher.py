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

from circuits import Component, Debugger
from circuits.web.websockets.dispatcher import WebSocketsDispatcher
from circuits.web import Server, Static
# from circuits.tools import graph

from hfos.web.objectmanager import ObjectManager
from hfos.web.rcmanager import RemoteControlManager
from hfos.web.clientmanager import ClientManager
from hfos.web.mapviewmanager import MapViewManager
from hfos.web.schemamanager import SchemaManager
from hfos.web.alertmanager import AlertManager
from hfos.web.layermanager import LayerManager
from hfos.web.auth import Authenticator
from hfos.web.chat import Chat
from hfos.web.tilecache import TileCache
from hfos.web.demo import WebDemo
from hfos.web.wiki import Wiki

from hfos.logger import hfoslog, verbose, setup_root, Logger
from hfos.debugger import HFDebugger

from hfos.protocols.nmea import NMEAParser, NMEAPlayback

from hfos.navdata import NavData


class App(Component):
    """HFOS Core Backend Application"""

    def __init__(self):
        super(App, self).__init__()
        hfoslog("[HFOS] Booting.")

    def started(self, component):
        """Sets up the application after startup."""
        hfoslog("[HFOS] Running.")
        hfoslog("[HFOS] Started event origin: ", component, lvl=verbose)


def main():
    """Preliminary HFOS application Launcher"""

    server = Server(("0.0.0.0", 8055))
    setup_root(server)
    Logger().register(server)
    hfoslog("[HFOS] Beginning graph assembly.")

    HFDebugger().register(server)

    app = App().register(server)

    # Machineroom().register(app)

    navdata = NavData().register(server)
    nmeaparser = NMEAParser('localhost', 2222).register(navdata)
    NMEAPlayback('/home/riot/tmp/nmea.log').register(nmeaparser)

    TileCache().register(server)
    Static("/", docroot="/var/lib/hfos/static").register(server)
    WebSocketsDispatcher("/websocket").register(server)

    clientmanager = ClientManager().register(server)
    AlertManager().register(clientmanager)
    SchemaManager().register(clientmanager)
    ObjectManager().register(clientmanager)
    Authenticator().register(clientmanager)
    Chat().register(clientmanager)
    MapViewManager().register(clientmanager)
    LayerManager().register(clientmanager)
    RemoteControlManager().register(clientmanager)
    WebDemo().register(clientmanager)
    Wiki().register(clientmanager)
    # CameraManager().register(clientmanager)

    # Logger().register(server)

    # dbg = Debugger()
    # dbg.IgnoreEvents.extend(["write", "_write", "streamsuccess"])
    # dbg.register(lm)

    # webbrowser.open("http://127.0.0.1:8055")

    # graph(server)

    hfoslog("[HFOS] Graph assembly done.")
    server.run()


if __name__ == "__main__":
    main()

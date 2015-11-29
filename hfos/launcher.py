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

from circuits import Component
from circuits.web.websockets.dispatcher import WebSocketsDispatcher

from circuits.web import Server, Static

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
from hfos.web.library import Library

from hfos.logger import hfoslog, verbose, setup_root, Logger
from hfos.debugger import HFDebugger


class App(Component):
    """HFOS Core Backend Application"""

    def __init__(self):
        super(App, self).__init__()
        hfoslog("[HFOS] Booting.")

    def started(self, component):
        """Sets up the application after startup."""
        hfoslog("[HFOS] Running.")
        hfoslog("[HFOS] Started event origin: ", component, lvl=verbose)


def construct_graph(dodebug=False, dograph=False, dogui=False):
    """Preliminary HFOS application Launcher"""

    server = Server(("0.0.0.0", 8055))
    setup_root(server)

    if dodebug:
        from circuits import Debugger

        dbg = Debugger()
        dbg.IgnoreEvents.extend(["write", "_write", "streamsuccess"])

        HFDebugger(root=server).register(server)

    Logger().register(server)
    hfoslog("[HFOS] Beginning graph assembly.")

    app = App().register(server)

    # Machineroom().register(app)

    # navdata = NavData().register(server)
    # NMEAParser('localhost', 2222).register(navdata)
    # NMEAPlayback('/home/riot/src/hfos/nmealog.txt', 1).register(navdata)

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
    Library().register(clientmanager)
    # CameraManager().register(clientmanager)

    # Logger().register(server)

    if dograph:
        from circuits.tools import graph

        graph(server)

    if dogui:
        import webbrowser

        webbrowser.open("http://127.0.0.1:8055")

    hfoslog("[HFOS] Graph assembly done.")

    return server


def run_graph(server):
    server.run()


def launch():
    server = construct_graph(dodebug=True)
    run_graph(server)

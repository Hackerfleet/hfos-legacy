#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2017 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "GPLv3"

"""

Module: ZMQ
===========

ZMQ connectors


"""
import random

from circuits import Timer, Worker, task
from hfos.database import objectmodels
from hfos.component import ConfigurableComponent, handler
from hfos.logger import hfoslog, hilight, error, warn, debug
from time import time
import threading

from netifaces import interfaces, ifaddresses, AF_INET
import zmq
from zmq.eventloop import ioloop, zmqstream

from pprint import pprint

PORT = 9000

ZMQHELLO = 1


class ZMQHandle(threading.Thread):
    def __init__(self, callback, sendcallback, peers, uuid):
        threading.Thread.__init__(self, daemon=True)
        hfoslog("Started", emitter="ZMQThread")

        self.loop = ioloop.IOLoop.instance()
        self.callback = callback
        self.peers = peers
        self.uuid = uuid
        self.sockets = {}
        self.routes = {}

        self.running = True
        self._stop = threading.Event()
        self.ctx = zmq.Context()
        sendcallback(self.send)

    def send(self, msg, uuid):
        hfoslog("Sending message: ", msg, " to ", uuid, emitter="ZMQThread")
        self.sockets[uuid].send_string(msg)

    def stop(self):
        hfoslog("Stopping loop",lvl=debug, emitter="ZMQThread")
        self.running = False
        self.loop.stop()
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def cb(self, data):
        hfoslog(data, emitter="ZMQThread")
        src = data[0]
        msg = data[1].decode('UTF8')
        if msg.startswith('OHAI'):
            hfoslog('OHAI received:', msg, emitter="ZMQThread")
        if msg.startswith('HELLO'):
            hfoslog("HELLO MESSAGE", emitter="ZMQThread")
            uuid = msg.split(':')[1]
            if src not in self.routes.keys():
                hfoslog("Unknown route, adding: ", uuid, emitter="ZMQThread")

                self.routes[uuid] = src
                hfoslog("Calling Callback", lvl=hilight, emitter="ZMQThread")

                self.callback({
                    'state': ZMQHELLO,
                    'uuid': uuid
                })
                hfoslog("Callback called.", lvl=hilight, emitter="ZMQThread")
            else:
                hfoslog("Duplicate Hello received", emitter="ZMQThread")
                if uuid not in self.routes.items():
                    hfoslog('Unknown UUID appeared on known route!', lvl=error, emitter="ZMQThread")
                else:
                    hfoslog('UUID appeared on another route!', lvl=warn, emitter="ZMQThread")
            hfoslog('Current routes:', self.routes, emitter="ZMQThread")

    def addNode(self, uuid, ip):
        hoststring = 'tcp://' + ip + ':' + str(PORT)
        hfoslog("ZMQ Dealer peer:", hoststring, emitter="ZMQThread")
        p = self.ctx.socket(zmq.DEALER)
        p.connect(hoststring)
        p.send_string('HELLO:' + self.uuid)
        self.sockets[uuid] = p

    def run(self):

        s = self.ctx.socket(zmq.ROUTER)

        s.bind("tcp://*:" + str(PORT))
        # s.setsockopt(zmq.SUBSCRIBE, b'')
        stream = zmqstream.ZMQStream(s, self.loop)
        stream.on_recv(self.cb)
        #print(s.getsockopt(zmq.LAST_ENDPOINT))

        for peer in self.peers:
            self.addNode(peer['uuid'], peer['ip'])

        hfoslog("Entering thread loop", lvl=debug, emitter="ZMQThread")
        self.loop.start()
        # from time import sleep
        # while self.running:
        #    sleep(0.1)
        hfoslog("Exiting thread loop", lvl=debug, emitter="ZMQThread")


class ZMQMesh(ConfigurableComponent):
    """
    Provides secure mesh based connectivity for HFOS nodes.
    """

    configprops = {}
    channel = 'zmq'

    def __init__(self, **kwargs):
        super(ZMQMesh, self).__init__('ZMQ', **kwargs)
        self.log("Started.")

        self.nodes = []
        self.hubs = []

        # self.interface = 'enp6s0'
        self.bcast = None

        self.uuid = None
        self.hub = False

        self._getHubs()
        self._getSystemData()
        self.connectednodes = []

        # inet = ifaddresses(self.interface)[AF_INET]
        # addr = inet[0]['addr']
        # masked = addr.rsplit('.', 1)[0]

        self.log('Started. Executing loop')
        self.send = None
        # result = yield self.call(task(handle, self.recv), 'zmqworkers')
        self.handler = ZMQHandle(self.recv, self.setcallback, self.hubs,
                                 self.uuid)
        self.handler.start()

        # self.send('Foobar', "2647d353-46c7-4ec7-a73d-9255da9162ef")

    def _getSystemData(self):
        systemconfig = objectmodels['systemconfig'].find_one({'active': True})
        self.uuid = systemconfig.uuid

    def _getHubs(self):
        nodes = objectmodels['meshnode']
        hubs = nodes.find({'hub': True})
        addresses = []

        for node in hubs:
            if node.uuid != self.uuid:
                addresses.append({'ip': node.address, 'uuid': node.uuid})
            else:
                self.hub = True
        self.log('Found hubs:', addresses)
        self.hubs = addresses

    def setcallback(self, cb):
        self.send = cb

    @handler('zmqpush', channel='zmq')
    def zmqpush(self, event):
        self.log('Talking!')
        self.send()

    def recv(self, event):
        self.log('ZMQ Received data', lvl=debug)
        if event['state'] == ZMQHELLO:
            self.log('New Node appeared')
            uuid = event['uuid']
            node = objectmodels['meshnode'].find_one({'uuid': uuid})
            if node is not None:
                self.log('Updating timestamp for node: ', uuid)
                node.last = time()
                node.save()
            else:
                self.log('Node is not known.')
            self.nodes.append(uuid)

        # stream.send_multipart(msg)
        self.log(event, lvl=debug)

        # self.log('WHOA: ', " ".join(event), event.__dict__)

    # def send(self):
    #    self.log('Sending data')
    #    msg = random.randint(0, 100)
    #    self.bcast.send_string("%s: %i" % (self.uniquename, msg))

    @handler("signal", channel="*")
    def _on_signal(self, signo, stack):
        if signo in [2, 15]:
            self.log('Stopping ZMQ sockets', lvl=debug)
            self.handler.stop()

"""

Module: Machineroom
===================

Engine, Rudder and miscellaneous machine roome control operations.

Currently this is only useable in conjunction with Hackerfleet's MS 0x00 NeoCortex board.

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from random import randint

import six

from circuits import Component, handler, Event
from circuits.io.events import write
from circuits.io import Serial

from hfos.logger import hfoslog, critical, debug


class MachineroomEvent(Event):
    def __init__(self, value, *args):
        super(MachineroomEvent, self).__init__(*args)
        self.controlvalue = value


class machine(MachineroomEvent):
    """Skipper wants us to change the engine speed/direction"""


class pump(MachineroomEvent):
    """Skipper wants us to turn on/off the coolant pump"""


class rudder(MachineroomEvent):
    """Skipper wants us to change the rudder angle"""


class Machineroom(Component):
    """
    Handles schemata requests from clients.
    """

    channel = "machineroom"

    servo = b's'
    pin = b'p'
    version = b'v'
    message = b'm'
    sep = b','
    if six.PY2:
        terminator = chr(13)
    else:
        terminator = bytes(chr(13), encoding="ascii")

    def __init__(self, port="/dev/ttyUSB0", baudrate=9600, buffersize=4096, *args):
        super(Machineroom, self).__init__(args)
        hfoslog("[MR] Machineroom starting")

        self._rudderchannel = 1
        self._machinechannel = 1
        self._pumpchannel = 3  # TODO: Make this a dedicated singleton call? e.g. pumpon/pumpoff.. not so generic

        Serial(port, baudrate, buffersize, timeout=5, channel="port").register(self)

        hfoslog("[MR] Running")

    def _sendcommand(self, command):
        cmd = command + self.terminator
        # cmdbytes = bytes(cmd, encoding="ascii")

        hfoslog("[MR] Transmitting bytes: ", "\n", cmd, lvl=critical)
        self.fireEvent(write(cmd), "port")

    @handler("opened", channel="port")
    def opened(self, *args):
        hfoslog("[MR] Opened: ", args, lvl=debug)
        self._sendcommand(b'l,1')  # Saying hello, shortly
        hfoslog("[MR] Turning off engine, pump and neutralizing rudder")
        self._sendcommand(b'v')
        self._handleServo(self._machinechannel, 0)
        self._handleServo(self._rudderchannel, 127)
        self._setDigitalPin(self._pumpchannel, 0)
        # self._sendcommand(b'h')
        self._sendcommand(b'l,0')
        self._sendcommand(b'm,HFOS Control')

    def _handleServo(self, channel, value):
        self._sendcommand(self.servo + self.sep + bytes([channel]) + self.sep + bytes([value]))

    def _setDigitalPin(self, pin, value):
        mode = 255 if value >= 127 else 0
        self._sendcommand(self.pin + self.sep + bytes([pin]) + self.sep + bytes([mode]))

    @handler("remotecontrolupdate")
    def on_remotecontrolupdate(self, event):
        hfoslog("[MR] Control updaterequest: ", event.controldata, lvl=critical)

    @handler("machine")
    def on_machinerequest(self, event):
        hfoslog("[MR] Updating new machine power: ", event.controlvalue)
        self._handleServo(self._machinechannel, event.controlvalue)

    @handler("rudder")
    def on_rudderrequest(self, event):
        hfoslog("[MR] Updating new rudder angle: ", event.controlvalue)
        self._handleServo(self._rudderchannel, event.controlvalue)

    @handler("pump")
    def on_pumprequest(self, event):
        hfoslog("[MR] Updating pump status: ", event.controlvalue)
        self._setDigitalPin(self._pumpchannel, event.controlvalue)

    @handler("read", channel="port")
    def read(self, *args):
        hfoslog("[MR] Data received from machineroom: ", args)

    @handler("ping")
    def on_ping(self):
        hfoslog("[MR] Pinging")
        self._handleServo(self._rudderchannel, randint(0, 255))

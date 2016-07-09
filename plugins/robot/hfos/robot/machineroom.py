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
import sys, glob

import six
from circuits import handler, Event
from circuits.io.events import write
from circuits.io import Serial
from hfos.component import ConfigurableComponent
from hfos.logger import hfoslog, critical, debug, warn

try:
    import serial
except ImportError:
    serial = None
    hfoslog("No serialport found. Serial bus remote control devices will be "
         "unavailable, install requirements.txt!",
             lvl=critical, emitter="MR")

class MachineroomEvent(Event):
    """

    :param value:
    :param args:
    """

    def __init__(self, value, *args):
        super(MachineroomEvent, self).__init__(*args)
        self.controlvalue = value


class machine(MachineroomEvent):
    """Skipper wants us to change the engine speed/direction"""


class pump(MachineroomEvent):
    """Skipper wants us to turn on/off the coolant pump"""


class rudder(MachineroomEvent):
    """Skipper wants us to change the rudder angle"""


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system

        Courtesy: Thomas ( http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python )
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class Machineroom(ConfigurableComponent):
    """
    Handles schemata requests from clients.
    """

    channel = "machineroom"

    ports = serial_ports()
    configprops = {
        'baudrate': {
            'type': 'integer',
            'title': 'Baudrate',
            'description': 'Communication data rate',
            'default': 9600
        },
        'buffersize': {
            'type': 'integer',
            'title': 'Buffersize',
            'description': 'Communication buffer size',
            'default': 4096
        },
        'serialfile': {
            'enum': ports + [''],
            'title': 'Serial port device',
            'description': 'File descriptor to access serial port',
            'default': ''
        },
    }

    servo = b's'
    pin = b'p'
    version = b'v'
    message = b'm'
    sep = b','
    if six.PY2:
        terminator = chr(13)
    else:
        # noinspection PyArgumentList
        terminator = bytes(chr(13), encoding="ascii")

    def __init__(self, *args, **kwargs):
        super(Machineroom, self).__init__('MR', *args, **kwargs)
        self.log("Machineroom starting")

        self._rudderchannel = 1
        self._machinechannel = 1
        self._pumpchannel = 3  # TODO: Make this a dedicated singleton call? e.g. pumpon/pumpoff.. not so generic
        self._serialopen = False

        if self.config.serialfile != '':
            try:
                self.serial = Serial(self.config.serialfile, self.config.baudrate, self.config.buffersize, timeout=5,
                                     channel="port").register(self)
            except Exception as e:
                self.log("Problem with serial port: ", e, type(e), lvl=critical)
        else:
            self.log("No serial port configured!", lvl=warn)

        self.log("Running")

    def _sendcommand(self, command):
        if not self._serialopen:
            self.log("Cannot transmit, serial port not available!", lvl=warn)
            return

        cmd = command + self.terminator
        # cmdbytes = bytes(cmd, encoding="ascii")

        self.log("Transmitting bytes: ", "\n", cmd, lvl=critical)
        self.fireEvent(write(cmd), "port")

    @handler("opened", channel="port")
    def opened(self, *args):
        """Initiates communication with the remote controlled device.

        :param args:
        """
        self._serialopen = True

        self.log("Opened: ", args, lvl=debug)
        self._sendcommand(b'l,1')  # Saying hello, shortly
        self.log("Turning off engine, pump and neutralizing rudder")
        self._sendcommand(b'v')
        self._handleServo(self._machinechannel, 0)
        self._handleServo(self._rudderchannel, 127)
        self._setDigitalPin(self._pumpchannel, 0)
        # self._sendcommand(b'h')
        self._sendcommand(b'l,0')
        self._sendcommand(b'm,HFOS Control')

    def _handleServo(self, channel, value):
        """

        :param channel:
        :param value:
        """
        self._sendcommand(self.servo + self.sep + bytes([channel]) + self.sep + bytes([value]))

    def _setDigitalPin(self, pin, value):
        """

        :param pin:
        :param value:
        """
        mode = 255 if value >= 127 else 0
        self._sendcommand(self.pin + self.sep + bytes([pin]) + self.sep + bytes([mode]))

    @handler("remotecontrolupdate")
    def on_remotecontrolupdate(self, event):
        """
        A remote control update request containing control data that has to be
        analysed according to the selected controller configuration.

        :param event: RemotecontrolUpdate
        """
        self.log("Control updaterequest: ", event.controldata, lvl=critical)

    @handler("machine")
    def on_machinerequest(self, event):
        """
        Sets a new machine speed.

        :param event:
        """
        self.log("Updating new machine power: ", event.controlvalue)
        self._handleServo(self._machinechannel, event.controlvalue)

    @handler("rudder")
    def on_rudderrequest(self, event):
        """
        Sets a new rudder angle.

        :param event:
        """
        self.log("Updating new rudder angle: ", event.controlvalue)
        self._handleServo(self._rudderchannel, event.controlvalue)

    @handler("pump")
    def on_pumprequest(self, event):
        """
        Activates or deactivates a connected pump.

        :param event:
        """
        self.log("Updating pump status: ", event.controlvalue)
        self._setDigitalPin(self._pumpchannel, event.controlvalue)

    @handler("read", channel="port")
    def read(self, *args):
        """
        Handles incoming data from the machine room hardware control system.

        :param args:
        """
        self.log("Data received from machineroom: ", args)

    @handler("ping")
    def on_ping(self):
        """
        Demo function for debugging purposes.

        """
        # TODO: Delete me
        self.log("Pinging")
        self._handleServo(self._rudderchannel, randint(0, 255))

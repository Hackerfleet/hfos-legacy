"""

Module: Machineroom
===================

Engine, Rudder and miscellaneous machine roome control operations.

Currently this is only useable in conjunction with Hackerfleet's MS 0x00
NeoCortex board.

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

import sys

import six
from circuits.io import Serial
from circuits.io.events import write
from random import randint

import glob
from hfos.component import ConfigurableComponent
from hfos.component import handler
from hfos.logger import hfoslog, critical, debug, warn

try:
    import serial
except ImportError:
    serial = None
    hfoslog("No serial port found. Serial bus remote control devices will be "
            "unavailable, install requirements.txt!",
            lvl=critical, emitter="MR")

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system

        Courtesy: Thomas ( http://stackoverflow.com/questions/12090503
        /listing-available-com-ports-with-python )
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
    Enables simple robotic control by translating high level events to
    servo control commands and transmitting them to a connected controller
    device.

    This prototype has built-in low level language support for the MS 0x00
    controller but can be easily adapted for other hardware servo/engine
    controllers.
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

        self._rudder_channel = 1
        self._machine_channel = 2
        self._pump_channel = 3  # TODO: Make this a dedicated singleton call?
        #  e.g. pumpon/pumpoff.. not so generic
        self._serial_open = False

        if self.config.serialfile != '':
            try:
                self.serial = Serial(self.config.serialfile,
                                     self.config.baudrate,
                                     self.config.buffersize, timeout=5,
                                     channel="port").register(self)
            except Exception as e:
                self.log("Problem with serial port: ", e, type(e),
                         lvl=critical)
        else:
            self.log("No serial port configured!", lvl=warn)

        self.log("Running")

    def _send_command(self, command):
        if not self._serial_open:
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
        self._serial_open = True

        self.log("Opened: ", args, lvl=debug)
        self._send_command(b'l,1')  # Saying hello, shortly
        self.log("Turning off engine, pump and neutralizing rudder")
        self._send_command(b'v')
        self._handle_servo(self._machine_channel, 0)
        self._handle_servo(self._rudder_channel, 127)
        self._set_digital_pin(self._pump_channel, 0)
        # self._send_command(b'h')
        self._send_command(b'l,0')
        self._send_command(b'm,HFOS Control')

    def _handle_servo(self, channel, value):
        """

        :param channel:
        :param value:
        """
        self._send_command(
            self.servo + self.sep + bytes([channel]) + self.sep + bytes(
                [value]))

    def _set_digital_pin(self, pin, value):
        """

        :param pin:
        :param value:
        """
        mode = 255 if value >= 127 else 0
        self._send_command(
            self.pin + self.sep + bytes([pin]) + self.sep + bytes([mode]))

    @handler("control_update")
    def on_control_update(self, event):
        """
        A remote control update request containing control data that has to be
        analysed according to the selected controller configuration.

        :param event: machine_update
        """
        self.log("Control update request: ", event.controldata, lvl=critical)

    @handler("machine")
    def on_machinerequest(self, event):
        """
        Sets a new machine speed.

        :param event:
        """
        self.log("Updating new machine power: ", event.controlvalue)
        self._handle_servo(self._machine_channel, event.controlvalue)

    @handler("rudder")
    def on_rudderrequest(self, event):
        """
        Sets a new rudder angle.

        :param event:
        """
        self.log("Updating new rudder angle: ", event.controlvalue)
        self._handle_servo(self._rudder_channel, event.controlvalue)

    @handler("pump")
    def on_pumprequest(self, event):
        """
        Activates or deactivates a connected pump.

        :param event:
        """
        self.log("Updating pump status: ", event.controlvalue)
        self._set_digital_pin(self._pump_channel, event.controlvalue)

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
        self._handle_servo(self._rudder_channel, randint(0, 255))

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2018 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from hfos.debugger import cli_register_event

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""


Module NavData
==============


"""

import time
import sys
import glob
from copy import copy
from circuits import Component, Timer, Event
from circuits.net.sockets import TCPClient
from circuits.net.events import connect, read
from circuits.io.serial import Serial
from decimal import Decimal
from hfos.component import ConfigurableComponent, LoggingComponent, handler
from hfos.database import ValidationError
from hfos.logger import hfoslog, verbose, debug, warn, critical, error, hilight
from hfos.misc import std_uuid
from hfos.navdata.events import sensordata

# from pprint import pprint



try:
    import serial
except ImportError:
    serial = None
    hfoslog(
        "[NMEA] No serialport found. Serial bus NMEA devices will be "
        "unavailable, install requirements.txt!",
        lvl=critical, emitter="NMEA")


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


def get_file_title_map(ports):
    title_map = {}
    for port in ports:
        title_map[port] = port

    return title_map


class serial_packet(Event):
    def __init__(self, bus, data, *args, **kwargs):
        super(serial_packet, self).__init__(*args, **kwargs)
        self.bus = bus
        self.data = data


class raw_data(serial_packet):
    pass


class detected_protocol(Event):
    def __init__(self, device, protocol, *args, **kwargs):
        super(detected_protocol, self).__init__(*args, **kwargs)
        self.device = device
        self.protocol = protocol


class register_protocol(Event):
    def __init__(self, name, keyword, *args, **kwargs):
        super(register_protocol, self).__init__(*args, **kwargs)
        self.protocol = name  # Also channel
        self.keyword = keyword


class restart_scan(Event):
    pass


class start_scanner(Event):
    pass


class scan_results(Event):
    def __init__(self, results, *args, **kwargs):
        super(scan_results, self).__init__(*args, **kwargs)
        self.results = results


class cli_bus_protocols(Event):
    """Display known bus protocols"""
    pass


class SerialBus(LoggingComponent):
    """Serial port connector that is aware of its connected interface"""

    def __init__(self, connection, *args, **kwargs):
        super(SerialBus, self).__init__(*args, **kwargs)
        self.log('Serial bus Component starting')

        self.bus = connection['bus']
        self.channel = "scanner_" + self.bus

        try:
            self.serial = Serial(
                connection['serialfile'],
                baudrate=connection.get('baudrate', 9600),
                channel=self.channel
            ).register(self)

        except serial.SerialException as e:
            self.log("Could not open configured port:",
                     connection['serialfile'], e,
                     lvl=error)

    def read(self, event, data):
        # self.log(data)
        self.fireEvent(serial_packet(self.bus, data), 'serial')


baudrates = [
    9600, 4800, 1200, 2400, 19200, 38400, 57600, 115200
]

baudrate_titlemap = [
    {'name': '1200', 'value': 1200},
    {'name': '2400', 'value': 2400},
    {'name': '4800', 'value': 4800},
    {'name': '9600', 'value': 9600},
    {'name': '19200', 'value': 19200},
    {'name': '38400', 'value': 38400},
    {'name': '57600', 'value': 57600},
    {'name': '115200', 'value': 115200},
]


class SerialBusManager(ConfigurableComponent):
    """
    Parses raw data (e.g. from a serialport) for NMEA data and sends single
    sentences out.
    """

    ports = serial_ports()

    configprops = {
        'scanner': {
            'type': 'object',
            'default': {'baud_rates': baudrates, 'timeout': 5, 'enabled': False},
            'properties': {
                'baud_rates': {
                    'type': 'array',
                    'items': {
                        'type': 'integer',
                    },
                    'default': baudrates,
                },
                'timeout': {
                    'type': 'integer',
                    'default': 5
                },
                'enabled': {
                    'type': 'boolean',
                    'default': False
                }
            }
        },
        'ports': {
            'type': 'array',
            'default': [],
            'items': {
                'type': 'object',
                'properties': {
                    'bus': {'type': 'string'},
                    'uuid': {'type': 'string'},
                    'connectiontype': {
                        'type': 'string',
                        'enum': ['TCP', 'USB/Serial'],
                        'title': 'Type of NMEA adaptor',
                        'description': 'Determines how to get data from the '
                                       'bus.',
                        'default': 'USB/Serial',
                        # TODO: Find out what causes this to be required (Form
                        # throws undecipherable errors without this)
                        # Same problem with the serialfile, below

                    },
                    'port': {
                        'type': 'number',
                        'title': 'TCP Port',
                        'description': 'Port to connect to',
                        'default': 2222
                    },
                    'host': {
                        'type': 'string',
                        'title': 'TCP Host',
                        'description': 'Host to connect to',
                        'default': 'localhost'
                    },
                    'serialfile': {
                        'type': 'string',
                        'title': 'Serial port device',
                        'description': 'File descriptor to access serial port',
                        'default': '',
                        'allowadditional': True,
                    },
                    'baudrate': {
                        'type': 'integer',
                        'title': 'Baudrate',
                        'description': 'Bus speed'
                    }
                }
            }
        }
    }

    configform = [
        {
            'key': 'scanner.baud_rates',
            'type': 'checkboxes',
            'titleMap': [

            ]
        },
        'scanner.timeout',
        {
            'title': 'Ports',
            'type': 'fieldset',
            'items': [
                {
                    'key': 'ports',
                    'add': 'Add Port',
                    'startEmpty': True,
                    'style': {
                        'add': 'btn-success'
                    },
                    'items': [
                        'ports[].bus',
                        {
                            'key': 'ports[].connectiontype',
                            'type': 'select',
                            'htmlClass': 'div',
                            'titleMap': {
                                'TCP': 'TCP',
                                'USB/Serial': 'USB/Serial'
                            }
                        },
                        {
                            'type': 'section',
                            'condition':
                                '$ctrl.model.ports['
                                'arrayIndex].connectiontype == '
                                '"USB/Serial"',
                            'htmlClass': 'row',
                            'items': [
                                {
                                    'htmlClass': 'col-md-6',
                                    'key': 'ports[].serialfile',
                                    'type': 'select',
                                    'titleMap': get_file_title_map(ports)
                                },
                                {
                                    'htmlClass': 'col-md-6',
                                    'key': 'ports[].baudrate',
                                    'type': 'select',
                                    'titleMap': baudrate_titlemap
                                }
                            ]
                        },
                        {
                            'type': 'section',
                            'condition': '$ctrl.model.ports['
                                         'arrayIndex'
                                         '].connectiontype == '
                                         '"TCP"',
                            'items': [
                                'ports[].host',
                                'ports[].port'
                            ]
                        }
                    ]
                }
            ]
        },
    ]

    channel = "serial"

    def __init__(self, *args, **kwargs):
        super(SerialBusManager, self).__init__('SERIALBUS', *args, **kwargs)

        self.log("Started")

        # self.bus = 'UNKNOWN'

        self.connections = {}

        self.unhandled = []
        self.unparseable = []

        self.scanning = False
        self.scanning_ports = {}
        self.scan_rates = {}
        self.scan_results = {}

        self.protocols = {}

        self.fireEvent(cli_register_event('bus_protocols', cli_bus_protocols))

        if len(self.config.ports) == 0:
            self.log('No ports configured', lvl=warn)
            if self.config.scanner['enabled']:
                self.log('Scanning for protocols')
                self.start_scanner()

        for connection in self.config.ports:
            self.log('Setting up existing connections')
            if connection['connectiontype'] == 'USB/Serial' and \
                    connection['serialfile'] == '':
                self.log('No serial bus source specified', lvl=warn)
            else:
                self._setup_connection(connection)

    def cli_bus_protocols(self, *args):
        self.log(self.protocols, pretty=True)

    def _build_port_chain(self, connection):
        bus = SerialBus(connection).register(self)

        return bus

    def _scan_serial_port(self, port):
        analyser = SerialBus({'serialfile': port, 'bus': port}).register(self)

        if port not in self.scan_rates:
            self.scan_rates[port] = copy(self.config.scanner['baud_rates'])

        try:
            baudrate = self.scan_rates[port].pop(0)
        except IndexError:
            self.log('Scan instructed, but no more baudrates left:', port,
                     lvl=warn)
            return

        self.log("Now scanning on serial port:", port, '(', baudrate, 'bps)',
                 lvl=debug)

        try:
            serial = Serial(
                port,
                baudrate=baudrate,
                channel="scanner_" + port
            ).register(analyser)

            self.scanning_ports[port] = analyser
        except serial.SerialException as e:
            self.log("Could not open configured port:", port, e,
                     lvl=error)

    # def _scan_ip_port(self, host, port):
    #     name = str(host) + str(port)
    #     self.log('Now scanning on ip port:', name, lvl=debug)
    #     self.scanning_ip[name] = TCPClient(
    #         channel='scanner_' + name).register(self)
    #     self.fire(connect(self.config.host, self.config.port),
    #               channel='scanner_' + name)

    def _check_protocol(self, event):
        detected = []

        for key, item in self.protocols.items():
            if not isinstance(item, list):
                checks = [item]
            else:
                checks = item

            for check in checks:
                if check.encode('utf-8') in event.data:
                    detected.append(key)

        if event.bus_name in self.scanning_ports:
            self.log('Detected protocol on', event.bus_name, ':', key)
            if event.bus_name not in self.scan_results:
                self.scan_results = []

            self.scan_results[event.bus_name].append(key)

            self._unregister_scanner(event.bus_name)
            del self.scanning_ports[event.bus_name]
            del self.scan_rates[event.bus_name]
        else:
            self.log('Scanner not registered (anymore)', lvl=verbose)

    def _unregister_scanner(self, device):
        self.log('Unregistering scanner', lvl=verbose)
        detector = self.scanning_ports[device]
        detector.stop()
        detector.unregister()

    @handler('register_protocol')
    def register_protocol(self, event):
        self.log('Registering scanner protocol:', event.protocol)
        self.protocols[event.protocol] = event.keyword

    @handler('restart_scan')
    def restart_scan(self, event):
        self.log('Restarting scan with new parameters', lvl=verbose)
        deleted = []

        for device in self.scanning_ports.keys():
            self._unregister_scanner(device)
            if len(self.scan_rates[device]) > 0:
                self._scan_serial_port(device)
            else:
                deleted.append(device)

        for device in deleted:
            self.scan_results[device] = []
            del self.scanning_ports[device]
            del self.scan_rates[device]

        if len(self.scanning_ports) > 0:
            Timer(self.config.scanner['timeout'], restart_scan()).register(self)
        else:
            self.log('Scan done. Found protocols:', self.scan_results)
            self.fireEvent(scan_results(self.scan_results))

    @handler('start_scanner')
    def start_scanner(self, *args):
        self.log('Initiating scan')
        scanning = False

        portlist = serial_ports()
        self.log('Scanning all found devices.', lvl=debug)

        self.log('Scanning', portlist, lvl=debug)
        for port in portlist:
            if port.startswith('/dev'):
                self._scan_serial_port(port)
                scanning = True
            else:
                self.log('Cannot yet scan non serial ports', lvl=warn)

        if scanning:
            Timer(self.config.scanner['timeout'], restart_scan()).register(self)

    def _setup_connection(self, connection):
        self.log('Connecting bus ports')
        port_up = False
        endpoint = None
        bus = connection['bus']

        if connection['connectiontype'] == 'USB/Serial':
            self.log("Connecting to serial port:", connection['serialfile'],
                     lvl=debug)
            try:
                endpoint = self._build_port_chain(connection)
                port_up = True
            except serial.SerialException as e:
                self.log("Could not open configured serial port:", e,
                         lvl=error)
        # elif connection['connectiontype'] == 'TCP':
        #     bus = connection['host'] + ":" + connection['port']
        #     endpoint = TCPClient(channel=self.channel).register(self)
        #
        #     port_up = True

        if port_up:
            self.log("Connection type", connection['connectiontype'],
                     "running. Bus known as", bus)
            self.connections[bus] = endpoint
        else:
            self.log("No port connected!", lvl=error)

    def ready(self, socket):
        for port in self.config.ports:
            if port.connectiontype == 'TCP':
                self.log("Connecting to tcp/ip serial bus service:",
                         port.host, ':', port.port, lvl=debug)
                self.fire(connect(port.host, port.port), )

    def _parse(self, bus, data):
        """
        Called when a sensor sends a new raw data to this serial connector.

        The data is sanitized and sent to the registered protocol
        listeners as time/raw/bus sentence tuple.
        """

        sen_time = time.time()

        try:
            # Split up multiple sentences
            if isinstance(data, bytes):
                data = data.decode('ascii')

            dirtysentences = data.split("\n")
            sentences = [(sen_time, x) for x in dirtysentences if x]

            def unique(it):
                s = set()
                for el in it:
                    if el not in s:
                        s.add(el)
                        yield el
                    else:
                        # TODO: Make sure, this is not identical but new data
                        self.log("Duplicate sentence received: ", el,
                                 lvl=debug)

            sentences = list(unique(sentences))
            return sentences
        except Exception as e:
            self.log("Error during data unpacking: ", e, type(e), lvl=error,
                     exc=True)

    def _broadcast(self, bus, sentences):
        try:
            self.log('Broadcasting raw sensordata', lvl=verbose)
            for sentence in sentences:
                for protocol, prefix in self.protocols.items():
                    self.log('sentence:', sentence[1], 'prefix:', prefix, lvl=verbose)
                    if sentence[1].startswith(prefix):
                        self.log('Distributing event', lvl=verbose)
                        self.fireEvent(raw_data(bus, sentence), protocol)

        except Exception as e:
            self.log("Error during parsing: ", e, lvl=critical)
            self.unparseable.append(sentences)

    def serial_packet(self, event):
        """Handles incoming raw sensor data
        :param data: raw incoming data
        """

        self.log('Incoming serial packet:', event.__dict__, lvl=verbose)

        if self.scanning:
            pass
        else:
            # self.log("Incoming data: ", '%.50s ...' % event.data, lvl=debug)
            sanitized_data = self._parse(event.bus, event.data)
            self.log('Sanitized data:', sanitized_data, lvl=verbose)
            if sanitized_data is not None:
                self._broadcast(event.bus, sanitized_data)

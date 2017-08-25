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


Module NavData
==============


"""

import sys
import glob
from copy import copy
from circuits import Component, Event, Timer
from circuits.net.sockets import TCPClient
from circuits.net.events import connect, read
from circuits.io.serial import Serial

from hfos.database import objectmodels  # , ValidationError
from hfos.events.system import authorizedevent
from hfos.navdata.events import referenceframe
from hfos.logger import hfoslog, events, debug, verbose, critical, warn, \
    error, hilight
from hfos.component import ConfigurableComponent, handler
from hfos.events.client import send, broadcast

from pprint import pprint

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
        except (OSError, serial.SerialException) as e:
            hfoslog('Could not open serial port:', port, e, type(e),
                    exc=True, lvl=warn)
    return result


class subscribe(authorizedevent):
    """Subscribes from a navigation data subscription"""


class unsubscribe(authorizedevent):
    """Unsubscribes from a navigation data subscription"""


class sensed(authorizedevent):
    """Requests a list of sensed values"""


class start_scanner_user(authorizedevent):
    """Starts the sensor bus scanning"""


class stop_scanner(authorizedevent):
    """Stops the sensor bus scanning"""


class Sensors(ConfigurableComponent):
    """
    The NavData (Navigation Data) component receives new sensordata and
    generates a new :referenceframe:


    """
    channel = "navdata"

    configprops = {}

    def __init__(self, *args):
        """
        Initialize the navigation sensor data component.

        :param args:
        """

        super(Sensors, self).__init__('NAVDATA', *args)

        self.datatypes = {}

        for item in objectmodels['sensordatatype'].find():
            # self.log("Adding sensor datatype to inventory:", item)
            self.datatypes[item.name] = item

        self.log("Added %i sensordatatypes to inventory." % len(
            self.datatypes))

        if len(self.datatypes) == 0:
            self.log("No sensordatatypes found! You may need to install the "
                     "provisions again.", lvl=warn)

        self.sensed = {}

        self.referenceframe = {}  # objectmodels['sensordata']()
        self.referenceages = {}
        self.changed = False

        self.interval = 1
        self.passiveinterval = 10
        self.intervalcount = 0

        self.subscriptions = {}

        Timer(self.interval, Event.create('navdatapush'), self.channel,
              persist=True).register(self)

    @handler(sensed, channel='hfosweb')
    def sensed(self, event):
        sensed = []

        for value in self.sensed.values():
            sensed.append(value.serializablefields())

        packet = {
            'component': 'hfos.navdata.sensors',
            'action': 'sensed',
            'data': {
                'sensed': sensed
            }
        }

        self.log("Transmitting list of sensed values:", self.sensed)
        self.fireEvent(send(event.client.uuid, packet), 'hfosweb')

    @handler(subscribe, channel='hfosweb')
    def subscribe(self, event):
        self.log('Navdata subscription requested for', event.data)

        for item in event.data:
            if item in self.subscriptions:
                if event.client.uuid not in self.subscriptions[item]:
                    self.subscriptions[item].append(event.client.uuid)
                    self.log("Appended subscription for ", item)
                else:
                    self.log("Client was already subscribed for that "
                             "value", lvl=warn)
            else:
                self.subscriptions[item] = [event.client.uuid]
                self.log("Created new subscription for ", item)

    @handler(unsubscribe, channel='hfosweb')
    def unsubscribe(self, event):
        self.log('Navdata unsubscription requested for', event.data)

        for item in event.data:
            if item in self.subscriptions:
                if event.client.uuid in self.subscriptions[item]:
                    self.subscriptions[item].remove(event.client.uuid)
                    if len(self.subscriptions[item]) == 0:
                        del self.subscriptions[item]
                        self.log("Removed last subscription for ", item)
                    else:
                        self.log("Removed subscription for ", item)

    @handler('clientdisconnect', channel='hfosweb')
    def clientdisconnect(self, event):
        self.log('Deleting subscriptions for disconnected client', lvl=debug)
        empty = []
        for name, subscription in self.subscriptions.items():
            while event.clientuuid in subscription:
                subscription.remove(event.clientuuid)
            if len(subscription) == 0:
                self.log('Subscription removed. Last subscriber for ',
                         subscription)
                del subscription
                empty.append(name)
        for name in empty:
            self.subscriptions.pop(name)

    def sensordata(self, event):
        """
        Generates a new reference frame from incoming sensordata

        :param event: new sensordata to be merged into referenceframe
        """

        if len(self.datatypes) == 0:
            return

        data = event.data
        timestamp = event.timestamp
        # bus = event.bus

        # TODO: What about multiple busses? That is prepared, but how exactly
        # should they be handled?

        self.log("New incoming navdata:", data, lvl=verbose)

        for name, value in data.items():
            if name in self.datatypes:
                ref = self.datatypes[name]
                self.sensed[name] = ref

                if ref.lastvalue != str(value):
                    # self.log("Reference outdated:", ref._fields)

                    item = {
                        'value': value,
                        'timestamp': timestamp,
                        'type': name
                    }

                    self.referenceframe[name] = value
                    self.referenceages[name] = timestamp

                    # self.log("Subscriptions:", self.subscriptions, ref.name)
                    if ref.name in self.subscriptions:

                        packet = {
                            'component': 'hfos.navdata.sensors',
                            'action': 'update',
                            'data': item
                        }

                        self.log("Serving update: ", packet, lvl=verbose)
                        for uuid in self.subscriptions[ref.name]:
                            self.log("Serving to ", uuid, lvl=events)
                            self.fireEvent(send(uuid, packet),
                                           'hfosweb')

                    # self.log("New item: ", item)
                    sensordata = objectmodels['sensordata'](item)
                    # self.log("Value entry:", sensordata._fields)

                    if ref.record:
                        self.log("Recording updated reference:",
                                 sensordata._fields)
                        sensordata.save()

                    ref.lastvalue = str(value)
                    ref.timestamp = timestamp
            else:
                self.log("Unknown sensor data received!", data, lvl=warn)

    def navdatapush(self):
        """
        Pushes the current :referenceframe: out to clients.

        :return:
        """

        try:
            self.fireEvent(referenceframe({
                'data': self.referenceframe, 'ages': self.referenceages
            }), "navdata")
            self.intervalcount += 1

            if self.intervalcount == self.passiveinterval and len(
                    self.referenceframe) > 0:
                self.fireEvent(broadcast('users', {
                    'component': 'hfos.navdata.sensors',
                    'action': 'update',
                    'data': {
                        'data': self.referenceframe,
                        'ages': self.referenceages
                    }
                }), "hfosweb")
                self.intervalcount = 0
                # self.log("Reference frame successfully pushed.",
                # lvl=verbose)
        except Exception as e:
            self.log("Could not push referenceframe: ", e, type(e),
                     lvl=critical)


class ProtocolAnalyser(Component):
    protocols = {}

    def __init__(self, interface, *args, **kwargs):
        super(ProtocolAnalyser, self).__init__(*args, **kwargs)

        self.interface = interface
        self.channel = "scanner_" + interface

    def read(self, *event):
        detected = []

        for key, item in self.protocols.items():
            if not isinstance(item, list):
                checks = [item]
            else:
                checks = item

            for check in checks:
                if check.encode('utf-8') in event[0]:
                    detected.append(key)

        if len(detected) > 0:
            self.fireEvent(detected_protocol(self.interface, detected),
                           'hfosweb')


class detected_protocol(Event):
    def __init__(self, device, protocol, *args, **kwargs):
        super(detected_protocol, self).__init__(*args, **kwargs)
        self.device = device
        self.protocol = protocol


class register_scanner_protocol(Event):
    def __init__(self, name, keyword, *args, **kwargs):
        super(register_scanner_protocol, self).__init__(*args, **kwargs)
        self.protocol = name
        self.keyword = keyword


class restart_scan(Event):
    pass


class start_scanner(Event):
    pass


class scan_results(Event):
    def __init__(self, results, *args, **kwargs):
        super(scan_results, self).__init__(*args, **kwargs)
        self.results = results


class SensorScanner(ConfigurableComponent):
    channel = 'hfosweb'

    configprops = {
        'baud_rates': {
            'type': 'array',
            'items': {
                'type': 'integer'
            },
            'default': [9600, 4800, 1200, 2400, 19200, 38400, 57600, 115200]
        },
        'timeout': {
            'type': 'integer',
            'default': 5
        }
    }

    def __init__(self, *args, **kwargs):
        super(SensorScanner, self).__init__('SENSORSCAN', *args, **kwargs)
        self.log("Started")

        self.scanning = {}
        self.scan_rates = {}
        self.scan_results = {}

    def _scan_serial_port(self, port):
        analyser = ProtocolAnalyser(port).register(self)

        if port not in self.scan_rates:
            self.scan_rates[port] = copy(self.config.baud_rates)

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

            self.scanning[port] = analyser
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

    @handler('detected_protocol')
    def detected_protocol(self, event):
        if event.device in self.scanning:
            self.log('Detected protocol on', event.device, ':', event.protocol)
            self.scan_results[event.device] = event.protocol

            self._unregister_scanner(event.device)
            del self.scanning[event.device]
            del self.scan_rates[event.device]
        else:
            self.log('Scanner not registered (anymore)', lvl=verbose)

    def _unregister_scanner(self, device):
        self.log('Unregistering scanner', lvl=verbose)
        detector = self.scanning[device]
        detector.stop()
        detector.unregister()

    @handler('register_scanner_protocol')
    def register_scanner_protocol(self, event):
        self.log('Registering scanner protocol:', event)
        ProtocolAnalyser.protocols[event.protocol] = event.keyword

    @handler('restart_scan')
    def restart_scan(self, event):
        self.log('Restarting scan with new parameters', lvl=verbose)
        deleted = []

        for device in self.scanning.keys():
            self._unregister_scanner(device)
            if len(self.scan_rates[device]) > 0:
                self._scan_serial_port(device)
            else:
                deleted.append(device)

        for device in deleted:
            self.scan_results[device] = []
            del self.scanning[device]
            del self.scan_rates[device]

        if len(self.scanning) > 0:
            Timer(self.config.timeout, restart_scan()).register(self)
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
            Timer(self.config.timeout, restart_scan()).register(self)

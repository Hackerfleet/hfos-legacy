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

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""


Module BusRepeater
==================


"""
from circuits.net.sockets import TCPServer, UDPClient
from circuits.net.events import write

from hfos.logger import debug, verbose
from hfos.component import ConfigurableComponent, handler


class BusRepeater(ConfigurableComponent):
    """
    The BusRepeater component receives new raw sensor data and
    repeats it over configurable tcp/udp/other means.

    """
    channel = "bus_repeater"

    configprops = {
        'udp_endpoints': {
            'type': 'array',
            'title': 'UDP Endpoints',
            'description': 'Transmit NMEA data to these endpoints via UDP',
            'items': {
                'type': 'string',
                'title': 'Recipient IP Address'
            },
            'default': []
        },
        'tcp_enabled': {
            'type': 'boolean',
            'default': False,
            'title': 'TCP',
            'description': 'Check to enable TCP server'
        },
        'udp_enabled': {
            'type': 'boolean',
            'default': False,
            'title': 'UDP',
            'description': 'Check to enable UDP transmission'
        },
        'tcp_port': {
            'type': 'number',
            'default': 2947,
            'title': 'TCP socket port',
            'description': 'TCP Port number on which to listen for NMEA '
                           'clients'
        },
        'tcp_ip': {
            'type': 'string',
            'default': '127.0.0.1',
            'title': 'TCP socket ip',
            'description': 'TCP IP address on which to listen for NMEA clients'
        },
        'udp_port': {
            'type': 'number',
            'default': 2947,
            'title': 'UDP socket port',
            'description': 'UDP Port number for sending data to NMEA clients'
        },
        'udp_ip': {
            'type': 'string',
            # TODO: This should be initialized when
            #  left blank
            'default': '127.0.0.1',
            'title': 'UDP socket ip',
            'description': 'UDP IP address for sending data to NMEA clients'
        }
    }

    def __init__(self, *args):
        """
        Initialize the bus repeater component.

        :param args:
        """

        super(BusRepeater, self).__init__('BUSREPEATER', *args)

        self._tcp_socket = self._udp_socket = None
        self._connected_tcp_endpoints = []

        if self.config.tcp_port != 0 and \
            self.config.tcp_ip is not None and \
                self.config.tcp_enabled is True:
            address = self.config.tcp_ip + ':' + str(self.config.tcp_port)
            self.log('Opening listening socket on', address, lvl=debug)
            self._tcp_socket = TCPServer(
                address,
                channel=self.channel + '_tcp'
            ).register(self)
        if len(self.config.udp_endpoints) > 0 and \
                self.config.udp_enabled is True:
            address = self.config.udp_ip + ':' + str(self.config.udp_port)
            self.log('Registering udp socket on', address, lvl=debug)
            self._udp_socket = UDPClient(
                0,
                channel=self.channel + '_udp'
            ).register(self)

    @handler('read', channel='nmea')
    def read(self, data):
        """Handles incoming raw sensor data and broadcasts it to specified
        udp servers and connected tcp clients
        :param data: NMEA raw sentences incoming data
        """

        self.log('Received NMEA data:', data, lvl=debug)
        # self.log(data, pretty=True)

        if self._tcp_socket is not None and \
                len(self._connected_tcp_endpoints) > 0:
            self.log('Publishing data on tcp server', lvl=debug)
            for endpoint in self._connected_tcp_endpoints:
                self.fireEvent(
                    write(
                        endpoint,
                        bytes(data, 'ascii')),
                    self.channel + '_tcp'
                )

        if self._udp_socket is not None and \
                len(self.config.udp_endpoints) > 0:
            self.log('Publishing data to udp endpoints', lvl=debug)
            for endpoint in self.config.udp_endpoints:
                host, port = endpoint.split(":")
                self.log('Transmitting to', endpoint, lvl=verbose)
                self.fireEvent(
                    write(
                        (host, int(port)),
                        bytes(data, 'ascii')
                    ),
                    self.channel +
                    '_udp'
                )

    @handler('connect', channel='bus_repeater_tcp')
    def _on_connect(self, socket, host, port):
        self.log('TCP Client connected:', host, port, lvl=debug)
        self._connected_tcp_endpoints.append(socket)

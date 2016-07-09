"""


Module NMEA
===========

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

import time
import sys
import glob
from circuits import Component, Timer, Event
from circuits.net.sockets import TCPClient
from circuits.net.events import connect, read
from circuits.io.serial import Serial

from decimal import Decimal
from hfos.component import ConfigurableComponent

from hfos.database import ValidationError
from hfos.events import sensordata
from hfos.logger import hfoslog, verbose, debug, warn, critical, error, hilight

try:
    from pynmea2 import parse
except ImportError:
    parse = None
    hfoslog("No pynmea found, install requirements-optional.txt", lvl=warn,
            emitter="NMEA")

try:
    import serial
except ImportError:
    serial = None
    hfoslog("[NMEA] No serialport found. Serial bus NMEA devices will be unavailable, install requirements.txt!",
            lvl=critical, emitter="NMEA")



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


class NMEAParser(ConfigurableComponent):
    """
    Parses raw data (e.g. from a serialport) for NMEA data and sends single sentences out.
    """
    ports = serial_ports()
    configprops = {
        'connectiontype': {
            'enum': ['TCP', 'USB/Serial'],
            'title': 'Type of NMEA adaptor',
            'description': 'Determines how to get data from the bus.',
            'default': 'USB/Serial'
        },
        'port': {
            'type': 'integer',
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
            'enum': ports + [''],
            'title': 'Serial port device',
            'description': 'File descriptor to access serial port',
            'default': ports[0] if len(ports) > 0 else '',
            'allowadditional': True
        },
    }

    channel = "nmea"

    def __init__(self, *args, **kwargs):
        try:
            super(NMEAParser, self).__init__('NMEA', *args, **kwargs)
        except ValidationError:
            self.log('OUPS.', lvl=hilight)
            # TODO: This was meant for catching unavailable serial-devices.
            # Needs a better way of handling that.

        if not parse:
            self.log("NOT started.", lvl=warn)
            return
        self.log("Started")

        self.bus = 'UNKNOWN'

        self.unhandled = []
        self.unparsable = []

        portup = False
        if self.config.connectiontype == 'USB/Serial':
            self.log("Connecting to serial port:", self.config.serialfile, lvl=debug)
            try:
                self.serial = Serial(self.config.serialfile, channel=self.channel).register(self)
                self.bus = self.config.serialfile
                portup = True
            except serial.SerialException as e:
                self.log("Could not open configured serial port:", e,
                         lvl=error)
        elif self.config.connectiontype == 'TCP':
            self.tcpclient = TCPClient(channel=self.channel).register(self)
            self.bus = self.config.host + ":" + self.config.port
            portup = True

        if portup:
            self.log("Connection type", self.config.connectiontype,
                     "running. Bus known as ", self.bus)
        else:
            self.log("No port connected!", lvl=error)

    def ready(self, socket):
        if self.config.connectiontype == 'TCP':
            self.log("Connecting to tcp/ip GPS network service:", self.config.host, ':', self.config.port, lvl=debug)
            self.fire(connect(self.config.host, self.config.port))

    def _parse(self, data):
        """
        Called when a publisher sends a new nmea sentence to this sensor.

        The nmea data is parsed and returned as NMEASentence object
        """

        nmeadata = []
        sen_time = time.time()

        try:
            # Split up multiple sentences
            if isinstance(data, bytes):
                data = data.decode('ascii')

            dirtysentences = data.split("\n")
            sentences = [x for x in dirtysentences if x]

            def unique(it):
                s = set()
                for el in it:
                    if el not in s:
                        s.add(el)
                        yield el
                    else:
                        self.log("Duplicate sentence received: ", el, lvl=debug)

            sentences = list(unique(sentences))
        except Exception as e:
            self.log("Error during data unpacking: ", e, type(e), lvl=error)
            return

        try:
            for sentence in sentences:
                if sentence[0] == '!':
                    # This is an AIS sentence or something else
                    self.log("Not yet implemented: AIS Sentence received.")
                else:
                    parsed_data = parse(sentence)
                    nmeadata.append(parsed_data)
        except Exception as e:
            self.log("Error during parsing: ", e, lvl=critical)
            self.unparsable.append(sentences)

        return nmeadata, sen_time

    def _handle(self, nmeadata):
        try:
            if len(nmeadata) == 0:
                self.log("Nothing to handle.", lvl=debug)
                return

            rawdata = {}
            for sentence in nmeadata:
                self.log("Sentence: ", sentence.fields, lvl=verbose)

                for item in sentence.fields:
                    itemname = item[1]
                    # hfoslog(itemname, lvl=critical)
                    value = getattr(sentence, itemname)
                    if value:
                        if len(item) == 3:
                            if item[2] in (Decimal, float):
                                value = float(value)
                            elif item[2] == int:
                                value = int(value)
                        #if sensordatatypes[itemname]['type'] == "string" or
                                #  (type(value) not in (str, int, float)):
                        #    value = str(value)
                        # hfoslog("{",itemname,": ",value, "}", lvl=critical)
                        rawdata.update({itemname: value})

                        # data.update(rawdata)
                        # hfoslog(data, lvl=critical)


                        # if type(sentence) in [types.GGA, types.GLL, types.GSV, types.MWD]:
                        #     data = sensordataobject()
                        #     data.Time_Created = sen_time
                        #     if type(sentence) == types.GGA:
                        #         data.GPS_LatLon = str((sentence.lat, sentence.lat_dir,
                        #                                sentence.lon, sentence.lon_dir))
                        #         data.GPS_SatCount = int(sentence.num_sats)
                        #         data.GPS_Quality = int(sentence.gps_qual)
                        #     elif type(sentence) == types.GLL:
                        #         data.GPS_LatLon = str((sentence.lat, sentence.lat_dir,
                        #                                sentence.lon, sentence.lon_dir))
                        #     elif type(sentence) == types.GSV:
                        #         data.GPS_SatCount = int(sentence.num_sv_in_view)
                        #     elif type(sentence) == types.MWD:
                        #         data.Wind_Direction_True = int(sentence.direction_true)
                        #         data.Wind_Speed_True = int(sentence.wind_speed_meters)

            return rawdata
            # else:
            #    self.log("Unhandled sentence acquired: ", sentence)
            #    if not type(sentence) in self.unhandled:
            #        self.unhandled.append(type(sentence))
        except Exception as e:
            self.log("Error during sending: ", nmeadata, e, type(e), lvl=error)

    def read(self, data):
        """Handles incoming raw sensor data
        :param data: NMEA raw sentences incoming data
        """

        if not parse:
            return

        #self.log("Incoming data: ", '%.50s ...' % data, lvl=debug)
        nmeadata, nmeatime = self._parse(data)

        #self.log("NMEA Parsed data:", nmeadata, lvl=debug)

        sensordatapackage = self._handle(nmeadata)


        #self.log("Sensor data:", sensordatapackage, lvl=debug)

        if sensordatapackage:
            self.fireEvent(sensordata(sensordatapackage, nmeatime, self.bus),
                       "navdata")
        # self.log("Unhandled data: \n", self.unparsable, "\n", self.unhandled, lvl=warn)


class NMEAPlayback(ConfigurableComponent):
    """
    Plays back previously recorded NMEA log files. Handy for debugging and demoing purposes.
    """

    configprops = {
        'delay': {
            'type': 'integer',
            'title': 'Delay',
            'description': 'Delay between messages (milliseconds)',
            'default': 5000
        },
        'logfile': {
            'type': 'string',
            'title': 'Filename',
            'description': 'Name of log file to replay',
            'default': ''
        },
    }

    channel = "nmea"

    def __init__(self, *args, **kwargs):
        super(NMEAPlayback, self).__init__('NMEAP', *args, **kwargs)
        self.log("Playback component started with", self.config.delay, "seconds interval.")

        if self.config.logfile != '':
            with open(self.config.logfile, 'r') as logfile:
                self.logdata = logfile.readlines()
            self.length = len(self.logdata)

            self.log("Logfile contains", self.length, "items.")

            self.position = 0

            Timer(self.config.delay/1000.0, Event.create('nmeaplayback'),
                  self.channel, persist=True).register(self)
        else:
            self.log("No logfile specified.", lvl=warn)

    def nmeaplayback(self, *args):
        self.log("Playback time", lvl=verbose)
        try:
            if self.position == len(self.logdata):
                self.log("Playback looping", lvl=warn)
                self.position = 0
            else:
                self.position += 1

            data = self.logdata[self.position]

            self.log("Transmitting: ", data, lvl=verbose)

            self.fireEvent(read(data), "nmea")

            if self.position % 100 == 0:
                self.log("Played back", self.position, "sentences.")

        except Exception as e:
            self.log("Error during logdata playback: ", e, type(e), lvl=error)

    def cliCommand(self, event):
        self.log('Executing CLI command: ', )

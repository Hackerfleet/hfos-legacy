"""


Module NMEA
===========

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

import time

from circuits import Component, Timer, Event
from circuits.net.sockets import TCPClient
from circuits.net.events import connect, read

from pynmea2 import parse
from pynmea2 import types

from hfos.database import sensordataobject
from hfos.events import sensordata
from hfos.logger import hfoslog, debug, warn, critical, error


class NMEAParser(Component):
    """
    Parses raw data (e.g. from a serialport) for NMEA data and sends single sentences out.
    """

    channel = "nmea"

    def init(self, host, port):
        hfoslog("[NMEA] Started")
        self.host = host
        self.port = port

        TCPClient(channel=self.channel).register(self)

    def ready(self, socket):
        hfoslog("[NMEA] Connecting...")
        self.fire(connect(self.host, self.port))

    def _parse(self, data):
        """
        Called when a publisher sends a new nmea sentence to this sensor.

        The nmea data is parsed and returned as NMEASentence object
        """

        nmeadata = []
        sen_time = time.time()

        try:

            # Split up multiple sentences
            dirtysentences = data.split("\n")
            sentences = [x for x in dirtysentences if x]

            def unique(it):
                s = set()
                for el in it:
                    if el not in s:
                        s.add(el)
                        yield el
                    else:
                        hfoslog("[NMEA] Duplicate sentence received: ", el, lvl=debug)

            sentences = list(unique(sentences))
        except Exception as e:
            hfoslog("[NMEA] Error during data unpacking: ", e, type(e), lvl=error)

        try:
            for sentence in sentences:
                parsed_data = parse(sentence)
                nmeadata.append((parsed_data, sen_time))
        except Exception as e:
            hfoslog("[NMEA] Error during parsing: ", e, lvl=critical)

        if len(nmeadata) > 0:
            hfoslog("[NMEA] Parsed sentences: ", len(nmeadata), lvl=debug)
            return nmeadata

    def _handle(self, nmeadata):

        for sentence, sen_time in nmeadata:
            try:
                if type(sentence) in [types.GGA, types.GLL, types.GSV, types.MWD]:
                    data = sensordataobject()
                    data.Time_Created = sen_time
                    if type(sentence) == types.GGA:
                        data.GPS_LatLon = str((sentence.lat, sentence.lat_dir,
                                               sentence.lon, sentence.lon_dir))
                        data.GPS_SatCount = int(sentence.num_sats)
                        data.GPS_Quality = int(sentence.gps_qual)
                    elif type(sentence) == types.GLL:
                        data.GPS_LatLon = str((sentence.lat, sentence.lat_dir,
                                               sentence.lon, sentence.lon_dir))
                    elif type(sentence) == types.GSV:
                        data.GPS_SatCount = int(sentence.num_sv_in_view)
                    elif type(sentence) == types.MWD:
                        data.Wind_Direction_True = int(sentence.direction_true)
                        data.Wind_Speed_True = int(sentence.wind_speed_meters)

                    self.fireEvent(sensordata(data), "navdata")
                else:
                    hfoslog("[NMEA] Unhandled sentence acquired: ", sentence)
            except Exception as e:
                hfoslog("[NMEA] Error during sending: ", nmeadata, e, type(e), lvl=error)

    def read(self, data):
        """Handles incoming raw sensor data
        :param data: NMEA raw sentences incoming data
        """

        hfoslog("[NMEA] Incoming data: ", '%.50s ...' % data, lvl=debug)
        nmeadata = self._parse(data)

        self._handle(nmeadata)



class NMEAPlayback(Component):
    """
    Plays back previously recorded NMEA log files. Handy for debugging and demoing purposes.
    """

    channel = "nmea"

    def init(self, logfilename, delay=5000):
        hfoslog("[NMEA] Playback component started")

        with open(logfilename, 'r') as logfile:
            self.logdata = logfile.readlines()

        hfoslog("[NMEA] Logfile contains ", len(self.logdata), " items.")

        self.delay = delay
        self.position = 0

        Timer(self.delay, Event.create('nmeaplayback'), self.channel, persist=True).register(self)

    def nmeaplayback(self,*args):
        try:
            if self.position == len(self.logdata):
                hfoslog("[NMEA] Playback looping")
                self.position = 0
            else:
                self.position += 1

            self.fireEvent(read(self.logdata[self.position]), "nmea")
        except Exception as e:
            hfoslog("[NMEA] Error during logdata playback: ", e, type(e), lvl=error)
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
from hfos.schemata.sensordata import sensordatatypes
from decimal import Decimal

from hfos.database import sensordataobject
from hfos.events import sensordata
from hfos.logger import hfoslog, verbose, debug, warn, critical, error


class NMEAParser(Component):
    """
    Parses raw data (e.g. from a serialport) for NMEA data and sends single sentences out.
    """

    channel = "nmea"

    def init(self, host, port):
        hfoslog("[NMEA] Started")
        self.host = host
        self.port = port

        self.unhandled = []
        self.unparsable = []

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
                if sentence[0] == '!':
                    # This is an AIS sentence or something else
                    hfoslog("[NMEA] Not yet implemented: AIS Sentence received.")
                else:
                    parsed_data = parse(sentence)
                    nmeadata.append((parsed_data, sen_time))
        except Exception as e:
            hfoslog("[NMEA] Error during parsing: ", e, lvl=critical)
            self.unparsable.append(sentences)

        return nmeadata

    def _handle(self, nmeadata):
        try:
            if len(nmeadata) == 0:
                hfoslog("[NMEA] Nothing to handle.", lvl=debug)
                return

            rawdata = {}
            for sentence, sen_time in nmeadata:
                hfoslog("[NMEA] Sentence: ", sentence.fields, lvl=verbose)

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
                        if sensordatatypes[itemname]['type'] == "string" or (type(value) not in (str, int, float)):
                            value = str(value)
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
            #    hfoslog("[NMEA] Unhandled sentence acquired: ", sentence)
            #    if not type(sentence) in self.unhandled:
            #        self.unhandled.append(type(sentence))
        except Exception as e:
            hfoslog("[NMEA] Error during sending: ", nmeadata, e, type(e), lvl=error)

    def read(self, data):
        """Handles incoming raw sensor data
        :param data: NMEA raw sentences incoming data
        """

        hfoslog("[NMEA] Incoming data: ", '%.50s ...' % data, lvl=debug)
        nmeadata = self._parse(data)

        data = sensordataobject(self._handle(nmeadata))

        self.fireEvent(sensordata(data), "navdata")
        #hfoslog("[NMEA] Unhandled data: \n", self.unparsable, "\n", self.unhandled, lvl=warn)



class NMEAPlayback(Component):
    """
    Plays back previously recorded NMEA log files. Handy for debugging and demoing purposes.
    """

    channel = "nmea"

    def init(self, logfilename, delay=5):
        hfoslog("[NMEAP] Playback component started with", delay,"seconds interval.")

        with open(logfilename, 'r') as logfile:
            self.logdata = logfile.readlines()
        self.length = len(self.logdata)

        hfoslog("[NMEAP] Logfile contains", self.length, "items.")

        self.delay = delay
        self.position = 0

        Timer(self.delay, Event.create('nmeaplayback'), self.channel, persist=True).register(self)

    def nmeaplayback(self, *args):
        hfoslog("[NMEAP] Playback time", lvl=verbose)
        try:
            if self.position == len(self.logdata):
                hfoslog("[NMEAP] Playback looping", lvl=warn)
                self.position = 0
            else:
                self.position += 1

            data = self.logdata[self.position]

            hfoslog("[NMEAP] Transmitting: ", data, lvl=verbose)

            self.fireEvent(read(data), "nmea")

            if self.position % 100 == 0:
                hfoslog("[NMEAP] Played back", self.position, "sentences.")

        except Exception as e:
            hfoslog("[NMEAP] Error during logdata playback: ", e, type(e), lvl=error)

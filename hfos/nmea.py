"""


Module NMEA
===========

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

import time

from circuits import Component
from pynmea.streamer import NMEAStream

from hfos.events import sensordata


class NMEAParser(Component):
    """
    Parses raw data (e.g. from a serialport) for NMEA data and sends single sentences out.
    """

    channel = "nmea"

    def __init__(self):
        super(NMEAParser, self).__init__()
        self.streamer = NMEAStream()
        # self.streamer.get_objects("\n")

    def _parse(self, data):
        """
        Called when a publisher sends a new nmea sentence to this sensor.

        The nmea data is parsed and returned as NMEASentence object
        """
        # sentences = []
        sen_time = time.time()

        # TODO: Something here is fishy, as in the first received packet
        # gets lost in the NMEAStream object. WTF.
        # (That was possibly an Axon initialization issue and should be fixed now)

        for sentence in self.streamer.get_objects(data, size=len(data) + 1):
            nmeadata = sentence.__dict__
            del (nmeadata['parse_map'])
            del (nmeadata['nmea_sentence'])
            nmeadata['time'] = sen_time
            nmeadata['type'] = sentence.sen_type
            # sentences.append(nmeadata)
            self.fireEvent(sensordata(nmeadata))

            # return sentences

    def read(self, *args):
        """Handles incoming raw sensor data
        :param args: Circuits Serial incoming data
        """

        data = args
        self._parse(data)

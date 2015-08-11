"""


Module NavData
==============

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from circuits import Component, Event, handler
from circuits import Timer

from hfos.database import sensordataobject, ValidationError
from hfos.events import referenceframe, broadcast
from hfos.logger import hfoslog, verbose, debug, warn, error, critical

from time import time
from json import dumps


class NavData(Component):
    channel = "navdata"

    def __init__(self, *args):
        super(NavData, self).__init__(*args)

        self.referenceframe = sensordataobject()
        self.referenceages = {}
        self.changed = False

        self.interval = 1
        self.passiveinterval = 10
        self.intervalcount = 0

        Timer(self.interval, Event.create('navdatapush'), self.channel, persist=True).register(self)

    def sensordata(self, event):
        newdata = event.data

        try:
            newdata.validate()
        except ValidationError as e:
            hfoslog("[NAVDATA] Invalid sensordata received: ", newdata, lvl=error)

        try:
            for key in newdata._fields:
                if key not in ('uuid', 'Time_Created'):
                    self.referenceframe._fields[key] = newdata._fields[key]
                    self.referenceages[key] = newdata._fields['Time_Created']

                    # hfoslog("[NAVDATA] New reference frame data: ", self.referenceages, self.referenceframe, lvl=critical)

        except Exception as e:
            hfoslog("[NAVDATA] Problem during sensordata evaluation: ", newdata, e, type(e), lvl=error)

    def navdatapush(self):

        try:
            self.fireEvent(referenceframe({'data': self.referenceframe, 'ages': self.referenceages}), "navdata")
            self.intervalcount += 1

            if self.intervalcount == self.passiveinterval:
                self.fireEvent(broadcast('users', {
                    'component': 'navdata',
                    'action': 'update',
                    'data': {
                        'data': self.referenceframe.serializablefields(),
                        'ages': self.referenceages
                    }
                }), "hfosweb")
                self.intervalcount = 0
            hfoslog("[NAVDATA] Reference frame successfully pushed.", lvl=verbose)
        except Exception as e:
            hfoslog("[NAVDATA] Could not push referenceframe: ", e, type(e), lvl=critical)

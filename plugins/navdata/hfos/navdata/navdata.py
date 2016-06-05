"""


Module NavData
==============

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from circuits import Event
from circuits import Timer
from hfos.database import objectmodels, ValidationError
from hfos.events import referenceframe, broadcast
from hfos.logger import hfoslog, verbose, error, critical

from hfos.component import ConfigurableComponent


class NavData(ConfigurableComponent):
    """
    The NavData (Navigation Data) component receives new sensordata and generates a new :referenceframe:


    """
    channel = "navdata"

    configprops = {}

    def __init__(self, *args):
        """
        Initialize the navigation data component.

        :param args:
        """

        super(NavData, self).__init__('NAVDATA', *args)

        self.referenceframe = objectmodels['sensordata']()
        self.referenceages = {}
        self.changed = False

        self.interval = 1
        self.passiveinterval = 10
        self.intervalcount = 0

        Timer(self.interval, Event.create('navdatapush'), self.channel, persist=True).register(self)

    def sensordata(self, event):
        """
        Generates a new reference frame from incoming sensordata

        :param event: new sensordata to be merged into referenceframe
        """
        newdata = event.data

        try:
            newdata.validate()
        except ValidationError as e:
            hfoslog("[NAVDATA] Invalid sensordata received: ", newdata, e, lvl=error)

            # TODO: Fix this weird stuff and get the navigational data aggregation running
            # try:
            #     for key in newdata._fields:
            #         if key not in ('uuid', 'Time_Created'):
            #             self.referenceframe._fields[key] = newdata._fields[key]
            #             self.referenceages[key] = newdata._fields['Time_Created']
            #
            #             # hfoslog("[NAVDATA] New reference frame data: ", self.referenceages, self.referenceframe, lvl=critical)
            #
            # except Exception as e:
            #     hfoslog("[NAVDATA] Problem during sensordata evaluation: ", newdata, e, type(e), lvl=error, exc=True)

    def navdatapush(self):
        """
        Pushes the current :referenceframe: out to clients.

        :return:
        """

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
                # hfoslog("[NAVDATA] Reference frame successfully pushed.",
                # lvl=verbose)
        except Exception as e:
            hfoslog("[NAVDATA] Could not push referenceframe: ", e, type(e), lvl=critical)

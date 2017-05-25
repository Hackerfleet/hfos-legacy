"""

Module: Navdata Simulator
=========================

A controllable navdata event simulation utility

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""
from hfos.navdata.events import sensordata

from hfos.component import ConfigurableComponent
from hfos.logger import error, warn, verbose, hilight
from circuits import Timer, Event
from hfos.component import handler
from time import time
from random import randint

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


class generatenavdata(Event):
    pass


class NavdataSim(ConfigurableComponent):
    """
    Event Playback

    Produces
    * outgoing events, that have previously been recorded to a readable json
    file
    """

    configprops = {}

    def __init__(self, *args):
        super(NavdataSim, self).__init__("NAVSIM", *args)

        if self.config.active is True:
            self.log("Started, channel:", self.channel)
            Timer(3, generatenavdata(), persist=True).register(self)
        else:
            self.log("Disabled.")

    @handler('generatenavdata')
    def generatenavdata(self, *args):
        self.log('Sending out simulated package.', lvl=verbose)
        data = {'DBT_depth_meters': randint(1, 250)}
        event = sensordata(data, time(), 'SIM')
        self.fireEvent(event, 'navdata')

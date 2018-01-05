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

Module: Vessel Simulator
========================

A controllable vessel event simulation utility


"""
import json
from circuits import Timer, Event

from hfos.navdata.events import updatevessel

from hfos.component import ConfigurableComponent
from hfos.logger import error, warn, verbose, hilight
from hfos.component import handler
from time import time
from pyproj import Geod

from pprint import pprint


class generatevesseldata(Event):
    pass


wgs84_geod = Geod(ellps='WGS84')


def Distance(lat1, lon1, lat2, lon2):
    """Get distance between pairs of lat-lon points"""

    az12, az21, dist = wgs84_geod.inv(lon1, lat1, lon2, lat2)
    return az21, dist


class VesselSim(ConfigurableComponent):
    """
    Event Playback

    Produces
    * outgoing events, that have previously been recorded to a readable json
    file
    """

    configprops = {}

    def __init__(self, *args):
        super(VesselSim, self).__init__("VESSELSIM", *args)

        if self.config.active is False:
            self.log("Disabled.")
            return

        self.vessels = {}
        self.start_time = time()

        self._load_vessel_data('/tmp/floatplan.json')

        self.log("Started, channel:", self.channel)
        Timer(3, generatevesseldata(), persist=True).register(self)
        write_float_plan()

    def _load_vessel_data(self, filename):
        with open(filename, 'r') as f:
            self.vesselplan = json.load(f)

        for name, item in self.vesselplan.items():
            self.log(item, lvl=hilight)
            self.vessels[item['uuid']] = item

        pprint(self.vessels)

    @handler('generatevesseldata')
    def generatevesseldata(self, *args):
        self.log('Sending out simulated package.', lvl=verbose)

        for uuid, vessel in self.vessels.items():
            
            speed = vessel['speed']
            distance = speed * (time() - self.start_time)
            a = self.vessels[uuid]['coordinates'][0]
            no = 1

            if len(self.vessels[uuid]['coordinates']) > no:
                continue

            while distance > 0:
                b = self.vessels[uuid]['coordinates'][no]
                angle, made_good = Distance(a[0], a[1], b[0], b[1])
                distance -= made_good
                a = b
                no += 1

            coordinate = a

            self.log('Distance left:', no, angle, distance, coordinate,
                 lvl=verbose)
        # event = updatevessel(time(), 'SIM')
        # self.fireEvent(event, 'navdata')


def write_float_plan():
    thing = {
        'Vessel A': {
            'uuid': 'a164abfc-7aeb-4bd4-a61b-db399a4206c4',
            'speed': 6.0,
            'coordinates': [
                [4.773559570312499, 53.32759237756109],
                [5.679931640625, 53.716215632472036],
                [6.4984130859375, 53.73246635451261],
                [6.85546875, 54.04648911335576],
                [7.8167724609375, 53.98193516209167],
                [7.921142578125, 54.1109429427243],
                [7.900457382202148, 54.170473659213776],
                [7.899341583251953, 54.17107657307259],
                [7.895479202270508, 54.17228237442875],
                [7.8941917419433585, 54.17343790107966]]
        },
        'Vessel B': {
            'uuid': '53283891-eff8-49da-9427-7884d86221ce',
            'speed': 12.0,
            'coordinates':
                [[7.894084453582764, 54.17367653843159],
                 [7.897946834564209, 54.17176740106635],
                 [7.89992094039917, 54.171440829270765],
                 [7.902131080627442, 54.17210653058677],
                 [7.902259826660156, 54.17304854244455],
                 [7.901916503906249, 54.173864935368464],
                 [7.901272773742676, 54.17494506124356],
                 [7.900328636169434, 54.17591212675687],
                 [7.899041175842284, 54.17657775611494],
                 [7.897024154663085, 54.17725593349987],
                 [7.895500659942626, 54.17777083853179],
                 [7.89365530014038, 54.178185269632806],
                 [7.8923892974853525, 54.17901411937589],
                 [7.892367839813232, 54.17960435073277],
                 [7.8922176361083975, 54.179729930785676],
                 [7.892518043518066, 54.17966714080689],
                 [7.892775535583496, 54.179466212234104],
                 [7.891981601715088, 54.17925272455584],
                 [7.89015769958496, 54.17859969658083],
                 [7.889277935028076, 54.17877551281926]]
        }
    }
    with open('/tmp/floatplan.json', 'w') as f:
        json.dump(thing, f)

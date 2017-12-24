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

Module: GuideManager
====================

Imports harbour & sailing guides from the web and keeps them up to date.

"""

import os
import json

from hfos.component import ConfigurableComponent, handler
from hfos.database import objectmodels
from hfos.logger import verbose, debug, error, warn, critical, events, hilight
from hfos.events.system import authorizedevent
from hfos.tools import std_uuid
from pprint import pprint

from urllib import request

try:
    from subprocess import Popen
except ImportError:
    from subprocess32 import Popen  # NOQA


class GuideManager(ConfigurableComponent):
    """
    """
    channel = "hfosweb"

    configprops = {
    }

    def __init__(self, *args):
        """
        Initialize the GuideManager component.

        :param args:
        """

        super(GuideManager, self).__init__("GUIDES", *args)

        self.translate_binary = '/usr/bin/ogr2ogr'
        self.cache_path = '/var/cache/hfos'

        self.log("Started")

        self.guides = {
            'skipperguide_german':
                'http://www.skipperguide.de/extension/GoogleEarthExport.php'
        }

        #self._update_guides()

    def _runcommand(self, command):
        self.log('Executing command: ', command, lvl=hilight)
        try:
            process = Popen(
                command,
                cwd=self.cache_path
            )

            process.wait()
        except Exception as e:
            self.log("Problem during gdal execution: ", command, e,
                     type(e), exc=True, lvl=error)
            return False
        return True

    def _translate(self, input_filename, output_filename):
        command = [
            self.translate_binary,
            '-f', 'GeoJSON',
            output_filename,
            input_filename
        ]

        result = self._runcommand(command)
        self.log('Result (Translate): ', result, lvl=hilight)

    def _update_guide(self, guide, update=False, clear=True):
        kml_filename = os.path.join(self.cache_path, guide + '.kml')
        geojson_filename = os.path.join(self.cache_path, guide + '.geojson')

        if not os.path.exists(geojson_filename) or update:
            try:
                data = request.urlopen(self.guides[guide]).read().decode(
                    'utf-8')
            except (request.URLError, request.HTTPError) as e:
                self.log('Could not get web guide data:', e, type(e), lvl=warn)
                return

            with open(kml_filename, 'w') as f:
                f.write(data)

            self._translate(kml_filename, geojson_filename)

        with open(geojson_filename, 'r') as f:
            json_data = json.loads(f.read())

        if len(json_data['features']) == 0:
            self.log('No features found!', lvl=warn)
            return

        layer = objectmodels['layer'].find_one({'name': guide})

        if clear and layer is not None:
            layer.delete()
            layer = None

        if layer is None:
            layer_uuid = std_uuid()
            layer = objectmodels['layer']({
                'uuid': layer_uuid,
                'name': guide,
                'type': 'geoobjects'
            })
            layer.save()
        else:
            layer_uuid = layer.uuid

        if clear:
            for item in objectmodels['geoobject'].find({'layer': layer_uuid}):
                self.log('Deleting old guide location',lvl=debug)
                item.delete()

        locations = []

        for item in json_data['features']:
            self.log('Adding new guide location:', item, lvl=verbose)
            location = objectmodels['geoobject']({
                'uuid': std_uuid(),
                'layer': layer_uuid,
                'geojson': item,
                'type': 'Skipperguide',
                'name': 'Guide for %s' % (item['properties']['Name'])
            })
            locations.append(location)

        self.log('Bulk inserting guide locations',lvl=debug)
        objectmodels['geoobject'].bulk_create(locations)

    def _update_guides(self):
        for guide in self.guides:
            self._update_guide(guide)

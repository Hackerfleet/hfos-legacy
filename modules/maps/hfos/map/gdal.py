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

Module: GDAL
============

Geospatial Data Abstraction Library support for HFOS.
 Uses tools from python-gdal to convert several popular map formats into
 tiledata usable with the map module.


"""

import os

from uuid import uuid4
# from circuits import Worker, task
from hfos.component import ConfigurableComponent, handler
from hfos.events.system import authorizedevent
from hfos.events.client import send
from hfos.database import objectmodels
from hfos.logger import error, verbose, warn, hilight
import datetime
import xml.etree.ElementTree

try:
    from subprocess import Popen
except ImportError:
    from subprocess32 import Popen  # NOQA


# TODO:
# * Thread the call to gdal utilities
# * Add grib import
#  * Grib conversion to tiles / vectors
#  * Grib layer creation
#  * GeoJSON delivery for vector data
# * Rename component to mapimporter

class UrlError(Exception):
    pass


class mapimport(authorizedevent):
    """Uploads a GDAL map file for conversion"""


class rescan(authorizedevent):
    """Triggers a rescan of the GDAL map folder"""


class GDAL(ConfigurableComponent):
    """
    Threaded, disk-caching tile delivery component
    """
    channel = "hfosweb"

    configprops = {}

    def __init__(self, path="/rastertiles",
                 tilepath="/var/cache/hfos/rastertiles",
                 storagepath="/var/cache/hfos/rastercache",
                 defaulttile=None, **kwargs):
        """

        :param path: Webserver path to offer cache on
        :param tilepath: Caching directory structure target path
        :param defaulttile: Used, when no tile can be cached
        :param kwargs:
        """
        super(GDAL, self).__init__('GDAL', **kwargs)

        # self.worker = Worker(process=False, workers=2,
        #                     channel="tcworkers").register(self)

        self.tilepath = tilepath
        self.storagepath = storagepath
        self.path = path
        self.defaulttile = defaulttile

        self.translate_binary = '/usr/bin/gdal_translate'
        self.tiler_binary = '/usr/bin/gdal2tiles.py'

        if (not os.path.exists(self.translate_binary) or not os.path.exists(
                self.tiler_binary)):
            self.log('No gdal tools found, will not be able to generate '
                     'tiles from foreign chart formats.', lvl=warn)

        self.log('Started')

    def _runcommand(self, command):
        self.log('Executing command: ', command, lvl=hilight)
        try:
            process = Popen(
                command,
                cwd=self.tilepath
            )

            process.wait()
        except Exception as e:
            self.log("Problem during gdal execution: ", command, e,
                     type(e), exc=True, lvl=error)
            return False
        return True

    def _translate(self, filename, temp_file):
        command = [
            self.translate_binary,
            '-of', 'vrt',
            '-expand', 'rgba',
            filename,
            temp_file
        ]

        result = self._runcommand(command)
        self.log('Result (Translate): ', result, lvl=hilight)

    def _tile(self, filename, target):

        command = [
            self.tiler_binary,
            '-w', 'none',
            filename
        ]

        result = self._runcommand(command)
        self.log('Result (Tiler): ', result, lvl=hilight)

    @handler(mapimport)
    def mapimport(self, event):
        self.log('Map import request!', lvl=hilight)

        name = event.data['name']
        self.log(name)

        # self.log(event.data['raw'])

        filename = os.path.join(self.storagepath, name)

        with open(filename, 'wb') as f:
            f.write(event.data['raw'])

        temp_file = filename.replace('.KAP', '.vrt')
        target = os.path.join(self.tilepath, name)

        self._translate(filename, temp_file)
        self._tile(temp_file, target)

        self.log('Done tiling: ', filename, target, lvl=hilight)

        newlayer = self._register_map(name.rstrip('.KAP'), target, event.client)

        notification = {
            'component': 'hfos.alert.manager',
            'action': 'success',
            'data': 'New rasterchart rendered: <a href="#!/editor/layer/' +
                    str(newlayer.uuid) + '/edit">' + newlayer.name + '</a>'
        }
        self.fireEvent(send(event.client.uuid, notification))

    @handler(rescan)
    def rescan(self, event):
        self.log('Rescanning gdal map folder for new maps')

        charts = []
        for (dirpath, dirnames, filenames) in os.walk(self.tilepath):
            charts.extend(dirnames)
            break

        self.log('Found folders:', charts, lvl=hilight)

        count = 0

        for chart in charts:
            target = os.path.join(self.tilepath, chart)
            if os.path.exists(os.path.join(target, 'tilemapresource.xml')):
                self.log('Raster chart found:', chart)
                layer = objectmodels['layer'].find_one({'path': chart})
                if layer is not None:
                    self.log('Layer exists: ', layer.uuid, layer.name)
                else:
                    self._register_map(chart, target, event.client)
                    count += 1
            else:
                self.log('Invalid raster tilecache found: ', chart, lvl=warn)

        if count > 0:
            data = 'Found and added %i new rasterchart' % count
            if count > 1:
                data += 's'
            data += ' during rasterchart rescan.'
        else:
            data = 'No new rastercharts added.'

        notification = {
            'component': 'hfos.alert.manager',
            'action': 'warning' if count == 0 else 'success',
            'data': data
        }
        self.fireEvent(send(event.client.uuid, notification))

    def _register_map(self, name, target, client):
        self.log('Storing new GDAL layer ', name, lvl=verbose)

        try:
            e = xml.etree.ElementTree.parse(
                os.path.join(target, 'tilemapresource.xml')).getroot()

            bounding_box = {
                'minx': None,
                'miny': None,
                'maxx': None,
                'maxy': None
            }

            if len(e.findall('BoundingBox')) != 1:
                self.log('Irregular bounding box definitions found:',
                         target, lvl=warn)
            for thing in e.findall('BoundingBox'):
                self.log('XMLBB:', thing, pretty=True, lvl=hilight)
                for key in bounding_box:
                    bounding_box[key] = float(thing.get(key))

            self.log('BOUNDING BOX:', bounding_box, pretty=True, lvl=hilight)

            zoomlevels = []
            for level in e.findall('TileSets')[0].findall('TileSet'):
                self.log("XMLTS:", level, pretty=True, lvl=hilight)
                zoomlevels.append(int(level.get('order')))

        except Exception as e:
            self.log('Problem during XML parsing:', e, type(e), exc=True)
            return

        layer = objectmodels['layer']({'uuid': str(uuid4())})
        layer.name = name
        layer.path = name
        layer.owner = client.useruuid
        layer.notes = "Imported GDAL chart"
        layer.description = "Imported GDAL chart '%s'" % name
        layer.type = 'xyz'
        layer.layerOptions = {
            'continuousWorld': False,
            'tms': True,
            'minZoom': min(zoomlevels),
            'maxZoom': max(zoomlevels),
            'bounds': [[bounding_box['miny'], bounding_box['minx']],
                       [bounding_box['maxy'], bounding_box['maxx']]]
        }
        layer.creation = datetime.datetime.now().isoformat()
        layer.url = 'http://hfoshost/rastertiles/' + name + '/{z}/{x}/{y}.png'

        layer.save()

        gdal_layers = objectmodels['layergroup'].find_one({
            'uuid': '6a18fdad-93a2-4563-bb8a-cb5888f43300'
        })

        gdal_layers.layers.append(layer.uuid)
        gdal_layers.save()

        self.log('New GDAL layer stored:', layer._fields, lvl=hilight)

        return layer

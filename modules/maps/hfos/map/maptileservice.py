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

Module: TileCache
=================

Autonomously operating local tilecache


"""

import socket
import os
import six
import errno

from copy import copy
from circuits import Worker, task, Event
from circuits.web.tools import serve_file

from hfos.component import ConfigurableController, ConfigurableComponent, \
    handler, authorizedevent
from hfos.events.client import send
from hfos.tools import std_uuid
from hfos.database import objectmodels, instance
from hfos.debugger import cli_register_event
from hfos.logger import error, verbose, warn, hilight

from .TileTools import TileFinder, TileUtils

from pprint import pprint
from time import sleep

if six.PY2:
    from urllib import unquote, urlopen
else:
    # noinspection PyCompatibility
    from urllib.request import urlopen  # NOQA
    # noinspection PyCompatibility
    from urllib.parse import unquote  # NOQA


def get_tile(url):
    """
    Threadable function to retrieve map tiles from the internet
    :param url: URL of tile to get
    """
    log = ""
    connection = None

    try:
        if six.PY3:
            connection = urlopen(url=url, timeout=2)  # NOQA
        else:
            connection = urlopen(url=url)
    except Exception as e:
        log += "MTST: ERROR Tilegetter error: %s " % str([type(e), e, url])

    content = ""

    # Read and return requested content
    if connection:
        try:
            content = connection.read()
        except (socket.timeout, socket.error) as e:
            log += "MTST: ERROR Tilegetter error: %s " % str([type(e), e])

        connection.close()
    else:
        log += "MTST: ERROR Got no connection."

    return content, log


class UrlError(Exception):
    pass


class request_maptile_area(authorizedevent):
    pass


class queue_trigger(authorizedevent):
    pass


class queue_cancel(authorizedevent):
    pass


class queue_remove(authorizedevent):
    pass


class cli_test_maptile_Loader(Event):
    """Test if the maptile cache loader works"""
    pass


class MaptileLoader(ConfigurableComponent):
    """
    Maptile offline loader component
    """

    configprops = {}

    channel = 'hfosweb'

    def __init__(self, tile_path=os.path.join('/var/cache/hfos', instance),
                 **kwargs):
        """

        :param tile_path: Caching directory structure target path
        :param default_tile: Used, when no tile can be cached
        :param kwargs:
        """
        super(MaptileLoader, self).__init__('MTL', **kwargs)

        self.worker = Worker(process=False, workers=2,
                             channel="tclworkers").register(self)

        self.cache_path = tile_path

        self.cancelled = []
        self.requests = {}

        self.fire(
            cli_register_event('test_maploader', cli_test_maptile_Loader))

    @handler("cli_test_maptile_Loader")
    def cli_test_maptile_loader(self, event, *args):
        self.log('Testing maptile loader')
        event = request_maptile_area(
            user=None, action=None, client=None,
            data={
                'layers': ['2837298e-a3e8-4a2e-8df2-f475554d2f23'],
                'extent': [-22, -22, -17, -17],
                'zoom': 14
            })
        self.fire(event)

    def _split_cache_url(self, url, url_type):
        try:
            # self.log('SPLITTING: ', url)
            url = url[len('/' + url_type):].lstrip('/')
            url = unquote(url)

            # self.log('SPLITDONE:', url)

            if '..' in url:  # Does this need more safety checks?
                self.log("Fishy url with parent path: ", url, lvl=error)
                raise UrlError

            split_url = url.split("/")
            service = "/".join(
                split_url[0:-3])  # get all but the coords as service
            # self.log('SERVICE:', service)

            x = split_url[-3]
            y = split_url[-2]
            z = split_url[-1].split('.')[0]

            filename = os.path.join(self.cache_path, url_type, service, x,
                                    y) + "/" + z + ".png"
            real_url = "http://%s/%s/%s/%s.png" % (service, x, y, z)
        except Exception as e:
            self.log("ERROR (%s) in URL: %s" % (e, url), exc=True)
            raise UrlError

        return filename, real_url

    @handler(request_maptile_area)
    def request_maptile_area(self, event):
        self.log("Offline caching for map area requested:", event.data)
        # constructing the template url for arcgis online

        extent = event.data['extent']
        zoom = event.data['zoom']

        layer_uuids = event.data['layers']

        tile_lists = {}

        tile_counter = 0

        for layer_uuid in layer_uuids:
            layer_object = objectmodels['layer'].find_one({'uuid': layer_uuid})
            if layer_object is None:
                self.log('Skipping non existing layer:', layer_uuid, lvl=warn)
                continue
            template = layer_object.url.split('hfoshost')[1]
            template = template.replace('{', '{{')
            template = template.replace('}', '}}')
            self.log('Template:', template)

            tileUtils = TileUtils()
            tileFinder = TileFinder(tileUtils, template)
            tile_urls = tileFinder.getTileUrlsByLatLngExtent(extent[0],
                                                             extent[1],
                                                             extent[2],
                                                             extent[3],
                                                             zoom)
            tile_lists[layer_uuid] = tile_urls
            tile_counter += len(tile_urls)

        size = tile_counter * 15
        self.log('About to get', tile_counter, 'tiles, estimated', size,
                 'kB')

        if tile_counter == 0:
            response = {
                'component': 'hfos.map.maptileservice',
                'action': 'empty',
                'data': "No tiles in that area to fetch"
            }
            self.fireEvent(send(event.client.uuid, response))

            return

        if size > 500:
            uuid = std_uuid()
            request = {
                'extent': extent,
                'uuid': uuid,
                'tiles': tile_counter,
                'completed': 0,
                'size': size,
                'lists': tile_lists
            }

            msg = "Estimated size of tile offloading queue exceeded 500 kB."

            self.log(msg, lvl=warn)
            self.requests[uuid] = request

            output = copy(request)
            output.pop('lists')

            response = {
                'component': 'hfos.map.maptileservice',
                'action': 'queued',
                'data': output
            }
            self.log('output:', output, pretty=True)
            self.fireEvent(send(event.client.uuid, response))

            return

    @handler(queue_cancel)
    def queue_cancel(self, event):
        self.log('Cancelling download of offline tiles')
        self.worker.pool.terminate()
        self.worker.unregister()
        self.worker = Worker(process=False, workers=2,
                             channel="tclworkers").register(self)

    @handler(queue_remove)
    def queue_remove(self, event):
        uuid = event.data

        try:
            queue = self.requests.pop(uuid)
            queue.pop('lists')
            response = {
                'component': 'hfos.map.maptileservice',
                'action': 'removed',
                'data': queue
            }
            self.fire(send(event.client.uuid, response))
        except ValueError:
            pass

    @handler(queue_trigger)
    def queue_trigger(self, event):
        uuid = event.data

        try:
            self.cancelled.remove(uuid)
        except ValueError:
            pass

        if uuid in self.requests:

            tile_lists = self.requests[uuid]['lists']

            self.log('Getting tile list')
            # TODO: Check if the layer is online at all
            #  e.g. rastercharts are not
            for layer_uuid, tile_urls in tile_lists.items():
                for url in tile_urls:
                    task = Event.create('get_tile_url',
                                        url=url,
                                        queue=uuid,
                                        layer=layer_uuid,
                                        client=event.client.uuid)
                    self.fire(task)

            response = {
                'component': 'hfos.map.maptileservice',
                'action': 'acting',
                'data': uuid
            }
            self.fireEvent(send(event.client.uuid, response))
        else:
            self.log('No queue request found:', uuid, lvl=warn)

    def get_tile_url(self, url, queue, layer, client):
        self.log('url:', url, queue, self.cancelled)
        if queue in self.cancelled:
            self.log('Not downloading tile due to cancellation')
            return

        filename, real_url = self._split_cache_url(url, 'tilecache')
        try:
            tile, log = yield self.call(task(get_tile, real_url), "tclworkers")
            if log != "":
                self.log("Thread error: ", log, lvl=error)
        except Exception as e:
            self.log("[MTS]", e, type(e))
            tile = None

        tile_path = os.path.dirname(filename)

        if tile:
            try:
                os.makedirs(tile_path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    self.log(
                        "Couldn't create path: %s (%s)" % (e, type(e)))

            self.log("Caching tile.", lvl=verbose)
            try:
                with open(filename, "wb") as tile_file:
                    try:
                        tile_file.write(bytes(tile))
                    except Exception as e:
                        self.log("Writing error: %s" % str([type(e), e]))

            except Exception as e:
                self.log("Open error: %s" % str([type(e), e]))
                return

            self.log("Tile stored.", lvl=verbose)

            self.requests[queue]['lists'][layer].remove(url)
            self.requests[queue]['completed'] += 1
            completed = self.requests[queue]['completed']

            if completed % 10 == 0:
                self.log('Sending progress report:', completed, '/',
                         self.requests[queue]['tiles'])
                progress_report = {
                    'component': 'hfos.map.maptileservice',
                    'action': 'offline_loader_progress',
                    'data': {
                        'queue': queue,
                        'completed': completed
                    }
                }
                self.fire(send(client, progress_report))
        else:
            self.log("Got no tile: %s" % real_url)


class MaptileService(ConfigurableController):
    """
    Threaded, disk-caching tile delivery component
    """

    configprops = {}

    def __init__(self, tile_path=os.path.join('/var/cache/hfos', instance), default_tile=None,
                 **kwargs):
        """

        :param tile_path: Caching directory structure target path
        :param default_tile: Used, when no tile can be cached
        :param kwargs:
        """
        super(MaptileService, self).__init__('MTS', **kwargs)
        self.worker = Worker(process=False, workers=2,
                             channel="tcworkers").register(self)

        self.cache_path = tile_path
        self.default_tile = default_tile
        self._tiles = []

    def _split_cache_url(self, url, url_type):
        try:
            # self.log('SPLITTING: ', url)
            url = url[len('/' + url_type):].lstrip('/')
            url = unquote(url)

            # self.log('SPLITDONE:', url)

            if '..' in url:  # Does this need more safety checks?
                self.log("Fishy url with parent path: ", url, lvl=error)
                raise UrlError

            split_url = url.split("/")
            service = "/".join(
                split_url[0:-3])  # get all but the coords as service
            # self.log('SERVICE:', service)

            x = split_url[-3]
            y = split_url[-2]
            z = split_url[-1].split('.')[0]

            filename = os.path.join(self.cache_path, url_type, service, x,
                                    y) + "/" + z + ".png"
            real_url = "http://%s/%s/%s/%s.png" % (service, x, y, z)
        except Exception as e:
            self.log("ERROR (%s) in URL: %s" % (e, url), exc=True)
            raise UrlError

        return filename, real_url

    def rastertiles(self, event, *args, **kwargs):
        request, response = event.args[:2]
        try:
            filename, url = self._split_cache_url(request.path, 'rastertiles')
        except UrlError as e:
            self.log('Rastertile cache url error:', e, exc=True, lvl=warn)
            return

        # self.log("RASTER QUERY:", filename, lvl=error)
        if os.path.exists(filename):
            return serve_file(request, response, filename)
        else:
            self.log('Non-existing raster tile request:', filename,
                     lvl=verbose)

    def tilecache(self, event, *args, **kwargs):
        """Checks and caches a requested tile to disk, then delivers it to
        client"""
        request, response = event.args[:2]
        self.log(request.path, lvl=verbose)
        try:
            filename, url = self._split_cache_url(request.path, 'tilecache')
        except UrlError:
            return

        # self.log('CACHE QUERY:', filename, url)

        # Do we have the tile already?
        if os.path.isfile(filename):
            self.log("Tile exists in cache", lvl=verbose)
            # Don't set cookies for static content
            response.cookie.clear()
            try:
                yield serve_file(request, response, filename)
            finally:
                event.stop()
        else:
            # We will have to get it first.
            self.log("Tile not cached yet. Tile data: ", filename, url,
                     lvl=verbose)
            if url in self._tiles:
                self.log("Getting a tile for the second time?!", lvl=error)
            else:
                self._tiles += url
            try:
                tile, log = yield self.call(task(get_tile, url), "tcworkers")
                if log:
                    self.log("Thread error: ", log, lvl=error)
            except Exception as e:
                self.log("[MTS]", e, type(e))
                tile = None

            tile_path = os.path.dirname(filename)

            if tile:
                try:
                    os.makedirs(tile_path)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        self.log(
                            "Couldn't create path: %s (%s)" % (e, type(e)))

                self.log("Caching tile.", lvl=verbose)
                try:
                    with open(filename, "wb") as tile_file:
                        try:
                            tile_file.write(bytes(tile))
                        except Exception as e:
                            self.log("Writing error: %s" % str([type(e), e]))

                except Exception as e:
                    self.log("Open error: %s" % str([type(e), e]))
                    return
                finally:
                    event.stop()

                try:
                    self.log("Delivering tile.", lvl=verbose)
                    yield serve_file(request, response, filename)
                except Exception as e:
                    self.log("Couldn't deliver tile: ", e, lvl=error)
                    event.stop()
                self.log("Tile stored and delivered.", lvl=verbose)
            else:
                self.log("Got no tile, serving default tile: %s" % url)
                if self.default_tile:
                    try:
                        yield serve_file(request, response, self.default_tile)
                    except Exception as e:
                        self.log('Cannot deliver default tile:', e, type(e),
                                 exc=True, lvl=error)
                    finally:
                        event.stop()
                else:
                    yield

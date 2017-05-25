"""

Module: TileCache
=================

Autonomously operating local tilecache

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

import socket
import os
import six
import errno
from circuits import Worker, task
from circuits.web.tools import serve_file
from hfos.component import ConfigurableController
from hfos.logger import error, verbose, warn

if six.PY2:
    from urllib import unquote, urlopen
else:
    # noinspection PyCompatibility
    from urllib.request import urlopen  # NOQA
    # noinspection PyCompatibility
    from urllib.parse import unquote  # NOQA

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


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


class MaptileService(ConfigurableController):
    """
    Threaded, disk-caching tile delivery component
    """

    configprops = {}

    def __init__(self, tile_path='/var/cache/hfos', default_tile=None,
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
                    finally:
                        event.stop()
                else:
                    yield

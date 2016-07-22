"""

Module: TileCache
=================

Autonomously operating local tilecache

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

import socket
import os
import six
import errno
from circuits import Worker, task
from circuits.web.tools import serve_file
from circuits.web.controllers import Controller
from hfos.logger import hfoslog, error, verbose

if six.PY2:
    from urllib import unquote, urlopen
else:
    from urllib.request import urlopen  # NOQA
    from urllib.parse import unquote  # NOQA

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


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


class MaptileService(Controller):
    """
    Threaded, disk-caching tile delivery component
    """
    # channel = "web"

    configprops = {}

    def __init__(self, path="/tilecache", tilepath="/var/cache/hfos/tilecache",
                 defaulttile=None, **kwargs):
        """

        :param path: Webserver path to offer cache on
        :param tilepath: Caching directory structure target path
        :param defaulttile: Used, when no tile can be cached
        :param kwargs:
        """
        super(MaptileService, self).__init__(**kwargs)
        self.worker = Worker(process=False, workers=2,
                             channel="tcworkers").register(self)

        self.tilepath = tilepath
        self.path = path
        self.defaulttile = defaulttile
        self._tilelist = []

    def _splitURL(self, url):
        try:
            if self.path is not None:
                url = url[len(self.path):]  # Cut off server's url path

            url = unquote(url)

            if '..' in url:  # Does this need more safety checks?
                hfoslog("Fishy url with parent path: ", url, lvl=error,
                        emitter="MTS")
                raise UrlError

            spliturl = url.split("/")
            service = "/".join(
                spliturl[1:-3])  # get all but the coords as service

            x = spliturl[-3]
            y = spliturl[-2]
            z = spliturl[-1].split('.')[0]

            filename = os.path.join(self.tilepath, service, x,
                                    y) + "/" + z + ".png"
            realurl = "http://" + service + "/" + x + "/" + y + "/" + z + \
                      ".png"
        except Exception as e:
            hfoslog("ERROR (%s) in URL: %s" % (e, url), emitter="MTS")
            raise UrlError

        return filename, realurl

    def tilecache(self, event, *args, **kwargs):
        """Checks and caches a requested tile to disk, then delivers it to
        client"""
        request, response = event.args[:2]
        try:
            filename, url = self._splitURL(request.path)
        except UrlError:
            return

        # Do we have the tile already?
        if os.path.isfile(filename):
            hfoslog("Tile exists in cache", emitter="MTS")
            # Don't set cookies for static content
            response.cookie.clear()
            try:
                yield serve_file(request, response, filename)
            finally:
                event.stop()
        else:
            # We will have to get it first.
            hfoslog("Tile not cached yet. Tile data: ", filename, url,
                    emitter="MTS")
            if url in self._tilelist:
                hfoslog("Getting a tile for the second time?!", lvl=error,
                        emitter="MTS")
            else:
                self._tilelist += url
            try:
                tile, log = yield self.call(task(get_tile, url), "tcworkers")
                if log:
                    hfoslog("Thread error: ", log, emitter="MTS")
            except Exception as e:
                hfoslog("[MTS]", e, type(e))
                tile = None

            tilepath = os.path.dirname(filename)

            if tile:
                try:
                    os.makedirs(tilepath)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        hfoslog("Couldn't create path: %s (%s)" % (e, type(e)),
                                exc=True, emitter="MTS")

                hfoslog("Caching tile.", lvl=verbose, emitter="MTS")
                try:
                    with open(filename, "wb") as tilefile:
                        try:
                            tilefile.write(bytes(tile))
                        except Exception as e:
                            hfoslog("Writing error: %s" % str([type(e), e]),
                                    emitter="MTS")

                except Exception as e:
                    hfoslog("Open error: %s" % str([type(e), e]),
                            emitter="MTS")
                    return
                finally:
                    event.stop()

                try:
                    hfoslog("Delivering tile.", lvl=verbose, emitter="MTS")
                    yield serve_file(request, response, filename)
                except Exception as e:
                    hfoslog("Couldn't deliver tile: ", e, lvl=error,
                            emitter="MTS")
                    event.stop()
                hfoslog("Tile stored and delivered.", lvl=verbose,
                        emitter="MTS")
            else:
                hfoslog("Got no tile, serving defaulttile: %s" % url,
                        emitter="MTS")
                if self.defaulttile:
                    try:
                        yield serve_file(request, response, self.defaulttile)
                    finally:
                        event.stop()
                else:
                    yield

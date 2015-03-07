"""
Hackerfleet Operating System - Backend

Module: TileCache
=================

Autonomously operating local tilecache

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

#!/usr/bin/env python

import socket

from circuits import Worker, task
from circuits.web.tools import serve_file
from circuits.web.controllers import Controller

import os

try:
    from urllib import quote, unquote, urlopen
except ImportError:
    print("V3")
    from urllib.request import urlopen
    from urllib.parse import quote, unquote  # NOQA


def get_tile(url, *args, **kwargs):
    """
    Threadable function to retrieve map tiles from the internet
    """
    log = "TC: INFO Getting tile: %s" % url

    connection = None

    try:
        connection = urlopen(url=url, timeout=5)
    except Exception as e:
        log += "TC: INFO Tilegetter error: %s " % str([type(e), e, url])

    content = ""

    # Read and return requested content
    if connection:
        try:
            content = connection.read()
        except (socket.timeout, socket.error) as e:
            log += "TC INFO Tilegetter error: %s " % str([type(e), e])

        connection.close()

    log += "TC INFO Tilegetter done."
    print(log)
    print(type(content), "%20s" % content)
    return content


class TileCache(Controller):
    """
    Threaded, disk-caching tile delivery component
    """
    #channel = "web"

    def __init__(self, path="/tilecache", tilepath="/var/cache/hfos/tilecache", defaulttile=None, **kwargs):
        """

        :param path: Webserver path to offer cache on
        :param tilepath: Caching directory structure target path
        :param defaulttile: Used, when no tile can be cached
        :param kwargs:
        """
        super(TileCache, self).__init__(**kwargs)
        Worker(process=False, workers=50, channel="tcworkers").register(self)

        self.tilepath = tilepath
        self.path = path
        self.defaulttile = defaulttile

    def tilecache(self, event, *args, **kwargs):
        """Checks and caches a requested tile to disk, then delivers it to client"""
        request, response = event.args[:2]

        origpath = request.path
        path = origpath

        if self.path is not None:
            path = path[len(self.path):]

        path = unquote(path)
        #print("TC: WARNING:  %s " % path)

        #if path:
        #    location = os.path.abspath(path)
        #else:
        #    print("TC: WARNING! This should not happen! Path was empty!")
        #    return

        #if not location.startswith(os.path.dirname(self.tilepath)):
        #    return  # hacking attemp e.g. /foo/../../../../../etc/shadow

        spliturl = path.split("/")
        #log("[TC] URL split", spliturl)
        service = "/".join(spliturl[1:-3])  # get all but the coords as service
        try:
            x = spliturl[-3]
            y = spliturl[-2]
            z = spliturl[-1].split('.')[0]

            filename = os.path.join(self.tilepath, service, x, y) + "/" + z + ".png"
            url = "http://" + service + "/" + x + "/" + y + "/" + z + ".png"
        except Exception as e:
            print("TC: ERROR (%s) in URL: %s" % (e, origpath))
            filename = ""
            url = ""

        # TODO: Clean up, restructure this

        # This check only necessary when leaflet is set continuousworld=true
        # (And it is not checking the upper bounds for x&y which are 2^z)
        # if (int(x) < 0 or int(y) < 0 or int(z) < 0):
        #    log("[TC] Illegal tile requested: ", url, lvl=warn)
        #    value['response'] = self.defaulttile

        # Do we have the tile already?
        if os.path.isfile(filename):
            print("TC: Tile exists in cache")
            # Don't set cookies for static content
            response.cookie.clear()
            try:
                yield serve_file(request, response, filename)
            finally:
                event.stop()
        else:
            # We will have to get it first.
            print("TC: Tile not cached yet.")
            print("TC: Estimated filename: %s " % filename)
            print("TC: Estimated URL: %s " % url)

            tile = yield self.call(task(get_tile, url), "tcworker")
            #print("#"*23+str(type(tile)), str(tile))
            #print(log)

            tilepath = os.path.dirname(filename)

            if tile:
                try:
                    os.makedirs(tilepath)
                except OSError as e:
                    print("TC: Couldn't create path: %s (%s)" % (e, type(e)))

                print("TC: Caching tile...")
                try:
                    tilefile = open(filename, "wb")
                except Exception as e:
                    print("TC: Open error: %s" % str([type(e), e]))
                    return

                try:
                    tilefile.write(bytes(tile))

                    tilefile.close()
                    yield serve_file(request, response, filename)
                except Exception as e:
                    print("TC: Writing error: %s" % str([type(e), e]))
                finally:
                    event.stop()
                print("TC: Tile stored and delivered.")
            else:
                print("TC: Got no tile, serving defaulttile: %s" % url)
                if self.defaulttile:
                    try:
                        yield serve_file(request, response, self.defaulttile)
                    finally:
                        event.stop()
                else:
                    yield

"""
Hackerfleet Operating System - Backend

Module: Mapviewstorage
======================

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

import json

from circuits import Component, handler

from hfos.events import send
from hfos.database import mapviewobject


class MapView(Component):
    """
    Handles mapview updates, subscriptions and broadcasts
    """
    channel = "mapview"

    def __init__(self, *args):
        super(MapView, self).__init__(*args)

        print("MVS: Started")
        self._subscribers = []

    def _broadcast(self, mapviewpacket):
        print("MVS: Transmitting message '%s'" % mapviewpacket)
        for recipient in self._subscribers[mapviewpacket['conent']['mapview'].uuid]:
            self.fireEvent(send(recipient.uuid, json.dumps(mapviewpacket)), "wsserver")

    @handler("mapviewupdaterequest")
    def on_mapviewupdaterequest(self, event):
        """
        Handles new mapview category requests

        Types:
        * subscribe
        * unsubscribe
        * update
        """

        print("MVS: Event: '%s'" % event.__dict__)
        try:
            useruuid = event.uuid
            requesttype = event.requesttype
            mapviewdata = event.mapview
            print("MVS: Request: '%s' Mapviewdata: %s" % (requesttype, mapviewdata))
            mapview = mapviewobject(mapviewdata)

            if requesttype == 'subscribe':
                # TODO: Verify everything and send a response
                self._subscribers[mapview.uuid].append(useruuid)
            if requesttype == 'unsubscribe':
                # TODO: Verify everything and send a response
                self._subscribers[mapview.uuid].remove(useruuid)
            if requesttype == 'update':

                dbmapview = None

                try:
                    dbmapview = mapviewobject.find_one({'uuid': useruuid})

                    dbmapview.update(mapview)
                    dbmapview.save()
                except Exception as e:
                    print("MVS: Database handling error: '%s' (%s)" % (e, type(e)))

                if dbmapview:
                    try:
                        mapviewpacket = {'type': 'mapviewupdate',
                                         'content': {
                                             'sender': useruuid,
                                             'mapview': dbmapview,
                                         }
                        }
                        self._broadcast(mapviewpacket)
                    except Exception as e:
                        print("MVS: Transmission error before broadcast: %s" % e)

                        #if msgtype == "part" and event.sender in self._clients:
                        #    self._clients.remove(event.sender)
                else:
                    print("MVS: Something horrible happened - i don't have a mapview object!")

        except Exception as e:
            print("MVS: Error: '%s' %s" % (e, type(e)))
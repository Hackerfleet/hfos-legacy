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

from hfos.events import send, broadcast

from hfos.database import mapviewobject
from hfos.logger import hfoslog, error


class MapView(Component):
    """
    Handles mapview updates, subscriptions and broadcasts
    """
    channel = "mapview"

    def __init__(self, *args):
        super(MapView, self).__init__(*args)

        hfoslog("MVS: Started")
        self._subscribers = {}

    def _broadcast(self, mapviewpacket, mapviewuuid):

        try:
            hfoslog("MVS: Transmitting message '%s'" % mapviewpacket)
            for recipient in self._subscribers[mapviewuuid]:
                self.fireEvent(send(recipient, mapviewpacket), "wsserver")
        except Exception as e:
            hfoslog("MVS: Failed broadcast: ", e, type(e), lvl=error)

    def _generatemapviewlist(self):
        try:
            result = {}
            for item in mapviewobject.find({'shared': True}):
                result[item.uuid] = item.serializablefields()
            return result
        except Exception as e:
            hfoslog("Error during list retrieval:", e, type(e), lvl=error)

    @handler("mapviewrequest")
    def on_mapviewrequest(self, event):
        """
        Handles new mapview category requests

        Types:
        * subscribe
        * unsubscribe
        * update
        """

        hfoslog("MVS: Event: '%s'" % event.__dict__)
        #try:
        try:
            try:
                userobj = event.sender
                useruuid = userobj.useruuid
                request = event.request
                hfoslog("MVS: Request raw: %s" % request)
                requesttype = request['type']
            except Exception as e:
                raise ValueError("MVS: Problem during event unpacking:", e, type(e))

            if requesttype == 'list':
                try:
                    dblist = self._generatemapviewlist()
                    self.fireEvent(send(useruuid, {'type': 'mapviewlist', 'content': dblist}), "wsserver")
                except Exception as e:
                    hfoslog("MVS: Listing error: ", e, type(e), lvl=error)
                return
            elif requesttype == 'get':
                dbmapview = None

                try:
                    dbmapview = mapviewobject.find_one({'uuid': useruuid})
                except Exception as e:
                    hfoslog("MVS: Get for MapView failed, creating new one.")

                if not dbmapview:
                    try:
                        try:
                            nickname = userobj.profile.nick
                        except AttributeError:
                            nickname = userobj.account.username
                        # TODO: Move this into a seperate operation (create)
                        dbmapview = mapviewobject({'uuid': useruuid,
                                                   'name': '%s Default MapView' % nickname,
                                                   'shared': True,
                        })
                        hfoslog("MVS: New mapviewobject: ", dbmapview)
                        dbmapview.save()
                    except Exception as e:
                        hfoslog("MVS: Storing new view failed: ", e, type(e), lvl=error)
                if dbmapview:
                    self.fireEvent(send(useruuid, {'type': 'mapviewget', 'content': dbmapview.serializablefields()}),
                                   "wsserver")

                return

            mapviewdata = request['mapview']
            mapviewuuid = mapviewdata['uuid']
            hfoslog("MVS: MapView request: '%s' Mapviewdata: %s" % (requesttype, mapviewdata))

            if requesttype == 'subscribe':
                # TODO: Verify everything and send a response
                if mapviewuuid in self._subscribers:
                    self._subscribers[mapviewuuid].append(useruuid)
                else:
                    self._subscribers[mapviewuuid] = [useruuid]
                return
            elif requesttype == 'unsubscribe':
                # TODO: Verify everything and send a response
                self._subscribers[mapviewuuid].remove(useruuid)
                if len(self._subscribers[mapviewuuid]) == 0:
                    del (self._subscribers[mapviewuuid])
                return
            elif requesttype == 'update':
                dbmapview = None
                hfoslog("MVS: Update begin")
                try:
                    dbmapview = mapviewobject.find_one({'uuid': useruuid})

                    dbmapview.update(mapviewdata)
                    dbmapview.save()
                    hfoslog("MVS: Valid update stored.")
                except Exception as e:
                    hfoslog("MVS: Database mapview not available. Looked for '%s' got error: '%s' (%s)" % (
                    useruuid, e, type(e)))

                if not dbmapview:
                    try:
                        hfoslog("MVS: New MapView: ", mapviewdata)
                        mapviewdata['uuid'] = useruuid  # make sure
                        dbmapview = mapviewobject(mapviewdata)
                        dbmapview.save()
                        hfoslog("MVS: New MapView stored.")

                        if dbmapview.shared:
                            hfoslog("MVS: Broadcasting list update for new mapview.")
                            self.fireEvent(broadcast("users", self._generatemapviewlist()), "wsserver")
                    except Exception as e:
                        hfoslog("MVS: MapView creation error: '%s' (%s)" % (e, type(e)))
                try:
                    hfoslog("MVS: Subscriptions: ", self._subscribers)
                    hfoslog("MVS: dbmapview: ", dbmapview._fields)
                    if dbmapview.shared:
                        if useruuid in self._subscribers:
                            try:
                                hfoslog("MVS: Broadcasting mapview update to subscribers.")
                                mapviewpacket = {'type': 'mapviewupdate',
                                                 'content': {
                                                     'sender': useruuid,
                                                     'mapview': dbmapview.serializablefields(),
                                                 }
                                }
                                self._broadcast(mapviewpacket, dbmapview.uuid)
                            except Exception as e:
                                hfoslog("MVS: Transmission error before broadcast: %s" % e)
                        else:
                            hfoslog("MVS: Not subscribed.")

                    else:
                        hfoslog("MVS: Not shared.")
                except Exception as e:
                    hfoslog("MVS: Update error during final mapview handling")

        except Exception as e:
            hfoslog("MVS: Global Error: '%s' %s" % (e, type(e)), lvl=error)
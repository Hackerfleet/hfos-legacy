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

from uuid import uuid4

from hfos.events import send, broadcast

from hfos.database import mapviewobject
from hfos.logger import hfoslog, error, warn, debug


class MapViewManager(Component):
    """
    Handles mapview updates, subscriptions and broadcasts
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(MapViewManager, self).__init__(*args)

        hfoslog("MVS: Started")
        self._subscribers = {}

    def _broadcast(self, mapviewpacket, mapviewuuid):

        try:
            hfoslog("MVS: Transmitting message '%s'" % mapviewpacket)
            for recipient in self._subscribers[mapviewuuid]:
                self.fireEvent(send(recipient, mapviewpacket))
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


    def _unsubscribe(self, clientuuid, mapuuid=None):
        # TODO: Verify everything and send a response
        if not mapuuid:
            for subscribers in self._subscribers.values():
                if clientuuid in subscribers:
                    subscribers.remove(clientuuid)
                    hfoslog("MVS: Subscription removed: ", clientuuid, lvl=debug)
        else:
            self._subscribers[mapuuid].remove(clientuuid)
            if len(self._subscribers[mapuuid]) == 0:
                del (self._subscribers[mapuuid])
                hfoslog("MVS: Subscription deleted: ", mapuuid, clientuuid)

    def client_disconnect(self, event):
        hfoslog("MVS: Removing disconnected client from subscriptions", lvl=debug)
        clientuuid = event.clientuuid
        self._unsubscribe(clientuuid)

    def mapviewrequest(self, event):
        """
        Handles new mapview category requests

        Types:
        * subscribe
        * unsubscribe
        * update
        """

        hfoslog("MVS: Event: '%s'" % event.__dict__)

        try:
            try:
                userobj = event.user
                action = event.action
                data = event.data

                useruuid = userobj.useruuid
                clientuuid = event.client.clientuuid
            except Exception as e:
                raise ValueError("MVS: Problem during event unpacking:", e, type(e))

            if action == 'list':
                try:
                    dblist = self._generatemapviewlist()
                    self.fireEvent(send(clientuuid, {'component': 'mapview', 'action': 'list', 'data': dblist}))
                except Exception as e:
                    hfoslog("MVS: Listing error: ", e, type(e), lvl=error)
                return
            elif action == 'get':
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
                        dbmapview = mapviewobject({'uuid': str(uuid4()),
                                                   'useruuid': useruuid,
                                                   'name': '%s Default MapView' % nickname,
                                                   'shared': True,
                        })
                        hfoslog("MVS: New mapviewobject: ", dbmapview)
                        dbmapview.save()
                    except Exception as e:
                        hfoslog("MVS: Storing new view failed: ", e, type(e), lvl=error)
                if dbmapview:
                    self.fireEvent(send(clientuuid, {'component': 'mapview', 'action': 'get',
                                                     'data': dbmapview.serializablefields()}))
                return
            elif action == 'subscribe':
                # TODO: Verify everything and send a response
                if data in self._subscribers:
                    if not clientuuid in self._subscribers[data]:
                        self._subscribers[data].append(clientuuid)
                else:
                    self._subscribers[data] = [clientuuid]
                hfoslog("MVS: Subscription registered: ", data, clientuuid)
                return
            elif action == 'unsubscribe':
                self._unsubscribe(clientuuid, data)
                return

            # The following need a mapview object attached

            try:
                mapview = mapviewobject(data)
                mapview.validate()
            except Exception as e:
                hfoslog("MVS: Only mapview related actions left, but no Mapviewobject.", e, type(e), lvl=warn)
                return

            if action == 'update':
                dbmapview = None
                hfoslog("MVS: Update begin")
                try:
                    uuid = mapview.uuid
                    dbmapview = mapviewobject.find_one({'uuid': uuid})
                    hfoslog(dbmapview.__dict__, lvl=error)
                except Exception as e:
                    hfoslog("MVS: Couldn't get mapview", (uuid, e, type(e)), lvl=error)
                    return

                try:

                    dbmapview.update(mapview._fields)
                    dbmapview.save()

                    hfoslog("MVS: Valid update stored.")
                except Exception as e:
                    hfoslog("MVS: Database mapview update failed: ", (uuid, e, type(e)), lvl=error)
                    return

                if not dbmapview:
                    try:
                        hfoslog("MVS: New MapView: ", mapview)
                        mapview.uuid = uuid  # make sure
                        mapview.save()
                        dbmapview = mapview
                        hfoslog("MVS: New MapView stored.")

                        if mapview.shared:
                            hfoslog("MVS: Broadcasting list update for new mapview.")
                            self.fireEvent(broadcast("users", self._generatemapviewlist()))
                    except Exception as e:
                        hfoslog("MVS: MapView creation error: '%s' (%s)" % (e, type(e)), lvl=error)
                        return

                try:
                    hfoslog("MVS: Subscriptions: ", self._subscribers)
                    hfoslog("MVS: dbmapview: ", mapview._fields)
                    if dbmapview.shared:
                        if dbmapview.uuid in self._subscribers:
                            try:
                                hfoslog("MVS: Broadcasting mapview update to subscribers.")
                                mapviewpacket = {'component': 'mapview',
                                                 'action': 'update',
                                                 'data': mapview.serializablefields()
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
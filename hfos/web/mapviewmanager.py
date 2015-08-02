"""


Module: Mapviewstorage
======================

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from uuid import uuid4

from circuits import Component

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

        hfoslog("[MVM] Started")
        self._subscribers = {}

    def _broadcast(self, mapviewpacket, mapviewuuid):

        try:
            hfoslog("[MVM] Transmitting message '%s'" % mapviewpacket)
            for recipient in self._subscribers[mapviewuuid]:
                self.fireEvent(send(recipient, mapviewpacket))
        except Exception as e:
            hfoslog("[MVM] Failed broadcast: ", e, type(e), lvl=error)

    def _generatemapviewlist(self):
        try:
            result = {}
            for item in mapviewobject.find({'shared': True}):
                result[item.uuid] = item.serializablefields()
            return result
        except Exception as e:
            hfoslog("[MVM] Error during list retrieval:", e, type(e), lvl=error)

    def _unsubscribe(self, clientuuid, mapuuid=None):
        # TODO: Verify everything and send a response
        if not mapuuid:
            for subscribers in self._subscribers.values():
                if clientuuid in subscribers:
                    subscribers.remove(clientuuid)
                    hfoslog("[MVM] Subscription removed: ", clientuuid, lvl=debug)
        else:
            self._subscribers[mapuuid].remove(clientuuid)
            if len(self._subscribers[mapuuid]) == 0:
                del (self._subscribers[mapuuid])
                hfoslog("[MVM] Subscription deleted: ", mapuuid, clientuuid)

    def client_disconnect(self, event):
        """Handles unsubscription of disconnected clients
        :param event:
        """

        hfoslog("[MVM] Removing disconnected client from subscriptions", lvl=debug)
        clientuuid = event.clientuuid
        self._unsubscribe(clientuuid)

    def mapviewrequest(self, event):
        """
        Handles new mapview category requests

        :param event: MapviewRequest with basic action types:
            * subscribe
            * unsubscribe
            * update
            * list
            * get
        """

        hfoslog("[MVM] Event: '%s'" % event.__dict__, lvl=debug)

        try:
            try:
                userobj = event.user
                action = event.action
                data = event.data
                try:
                    nickname = userobj.profile.nick
                except AttributeError:
                    nickname = userobj.account.username

                useruuid = userobj.uuid
                hfoslog("[MVM] client: ", event.client.__dict__)
                clientuuid = event.client.uuid
            except Exception as e:
                raise ValueError("[MVM] Problem during event unpacking:", e, type(e))

            if action == 'list':
                try:
                    dblist = self._generatemapviewlist()
                    self.fireEvent(send(clientuuid, {'component': 'mapview', 'action': 'list', 'data': dblist}))
                except Exception as e:
                    hfoslog("[MVM] Listing error: ", e, type(e), lvl=error)
                return
            elif action == 'get':
                dbmapview = None

                try:
                    dbmapview = mapviewobject.find_one({'uuid': useruuid})
                except Exception as e:
                    hfoslog("[MVM] Get for MapView failed, creating new one.", e)

                if not dbmapview:
                    try:
                        # TODO: Move this into a seperate operation (create)
                        dbmapview = mapviewobject({'uuid': str(uuid4()),
                                                   'useruuid': useruuid,
                                                   'name': '%s Default MapView' % nickname,
                                                   'shared': True,
                                                   })
                        hfoslog("[MVM] New mapviewobject: ", dbmapview)
                        dbmapview.save()
                    except Exception as e:
                        hfoslog("[MVM] Storing new view failed: ", e, type(e), lvl=error)
                if dbmapview:
                    self.fireEvent(send(clientuuid, {'component': 'mapview', 'action': 'get',
                                                     'data': dbmapview.serializablefields()}))
                return
            elif action == 'subscribe':
                try:
                    dbmapview = mapviewobject.find_one({'uuid': data})
                except Exception as e:
                    hfoslog("[MVM] Get for MapView failed. Creating new one.", e)

                if not dbmapview:
                    dbmapview = mapviewobject({'uuid': str(uuid4()),
                                               'useruuid': useruuid,
                                               'name': '%s Default MapView' % nickname,
                                               'shared': True,
                                               })

                if data in self._subscribers:
                    if clientuuid not in self._subscribers[data]:
                        self._subscribers[data].append(clientuuid)
                else:
                    self._subscribers[data] = [clientuuid]

                hfoslog("[MVM] Subscription registered: ", data, clientuuid, dbmapview.to_dict())

                self.fireEvent(send(clientuuid, {'component': 'mapview', 'action': 'get',
                                                 'data': dbmapview.serializablefields()}))

                return
            elif action == 'unsubscribe':
                self._unsubscribe(clientuuid, data)
                return

            # The following need a mapview object attached

            try:
                mapview = mapviewobject(data)
                mapview.validate()
            except Exception as e:
                hfoslog("[MVM] Only mapview related actions left, but no Mapviewobject.", e, type(e), lvl=warn)
                return

            if action == 'update':

                hfoslog("[MVM] Update begin")
                try:
                    uuid = mapview.uuid
                    dbmapview = mapviewobject.find_one({'uuid': uuid})
                    hfoslog("[MVM] Database Mapview dict: ", dbmapview.__dict__, lvl=error)
                except Exception as e:
                    hfoslog("[MVM] Couldn't get mapview", (data, e, type(e)), lvl=error)
                    return

                if dbmapview:
                    try:
                        dbmapview.update(mapview._fields)
                        dbmapview.save()

                        hfoslog("[MVM] Valid update stored.")
                    except Exception as e:
                        hfoslog("[MVM] Database mapview update failed: ", (uuid, e, type(e)), lvl=error)
                        return
                else:
                    try:
                        hfoslog("[MVM] New MapView: ", mapview)
                        mapview.uuid = uuid  # make sure
                        mapview.save()
                        dbmapview = mapview
                        hfoslog("[MVM] New MapView stored.")

                        if mapview.shared:
                            hfoslog("[MVM] Broadcasting list update for new mapview.")
                            self.fireEvent(broadcast("users", self._generatemapviewlist()))
                    except Exception as e:
                        hfoslog("[MVM] MapView creation error: '%s' (%s)" % (e, type(e)), lvl=error)
                        return

                try:
                    hfoslog("[MVM] Subscriptions: ", self._subscribers)
                    hfoslog("[MVM] dbmapview: ", mapview._fields)
                    if dbmapview.shared:
                        if dbmapview.uuid in self._subscribers:
                            try:
                                hfoslog("[MVM] Broadcasting mapview update to subscribers.")
                                mapviewpacket = {'component': 'mapview',
                                                 'action': 'update',
                                                 'data': mapview.serializablefields()
                                                 }
                                self._broadcast(mapviewpacket, dbmapview.uuid)
                            except Exception as e:
                                hfoslog("[MVM] Transmission error before broadcast: %s" % e)
                        else:
                            hfoslog("[MVM] Not subscribed.")

                    else:
                        hfoslog("[MVM] Not shared.")
                except Exception as e:
                    hfoslog("[MVM] Update error during final mapview handling", e)

        except Exception as e:
            hfoslog("[MVM] Global Error: '%s' %s" % (e, type(e)), lvl=error)

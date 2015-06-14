"""


Module: LayerManager
====================

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from circuits import Component

from hfos.events import send, broadcast
from hfos.database import layerobject
from hfos.logger import hfoslog, error


class LayerManager(Component):
    """
    Handles layer updates, subscriptions and broadcasts
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(LayerManager, self).__init__(*args)

        hfoslog("[LM] Started")
        self._subscribers = {}

    def _broadcast(self, layerupdatepacket, layeruuid):

        try:
            hfoslog("[LM] Transmitting message '%s'" % layerupdatepacket)
            for recipient in self._subscribers[layeruuid]:
                self.fireEvent(send(recipient, layerupdatepacket), "wsserver")
        except Exception as e:
            hfoslog("[LM] Failed broadcast: ", e, type(e), lvl=error)

    def _generatelayerlist(self):
        try:
            result = {}
            for item in layerobject.find({'shared': True}):
                result[item.uuid] = item.serializablefields()
            return result
        except Exception as e:
            hfoslog("[LM] Error during list retrieval:", e, type(e), lvl=error)

    def layerrequest(self, event):
        """
        Handles new layer category requests

        :param event: LayerRequest Event with basic action types:
        * put
        * get
        * delete
        * list

        For events, there are two more actions:
        * subscribe
        * unsubscribe

        """

        hfoslog("[LM] Event: '%s'" % event.__dict__)
        # try:
        try:
            try:
                userobj = event.sender
                useruuid = userobj.useruuid
                request = event.request
                hfoslog("[LM] Request raw: %s" % request)
                requesttype = request['type']
            except Exception as e:
                raise ValueError("[LM] Problem during event unpacking:", e, type(e))

            if requesttype == 'list':
                try:
                    dblist = self._generatelayerlist()
                    self.fireEvent(send(useruuid, {'type': 'layerlist', 'content': dblist}), "wsserver")
                except Exception as e:
                    hfoslog("[LM] Listing error: ", e, type(e), lvl=error)
                return
            elif requesttype == 'get':
                dblayer = None

                try:
                    dblayer = layerobject.find_one({'uuid': useruuid})
                except Exception as e:
                    hfoslog("[LM] Get for MapView failed, creating new one.", e)

                if not dblayer:
                    try:
                        try:
                            nickname = userobj.profile.nick
                        except AttributeError:
                            nickname = userobj.account.username
                        # TODO: Move this into a seperate operation (create)
                        dblayer = layerobject({'uuid': useruuid,
                                               'name': '%s Default MapView' % nickname,
                                               'shared': True,
                                               })
                        hfoslog("[LM] New layerobject: ", dblayer)
                        dblayer.save()
                    except Exception as e:
                        hfoslog("[LM] Storing new view failed: ", e, type(e), lvl=error)
                if dblayer:
                    self.fireEvent(send(useruuid, {'type': 'layerget', 'content': dblayer.serializablefields()}),
                                   "wsserver")

                return

            layerdata = request['layer']
            layeruuid = layerdata['uuid']
            hfoslog("[LM] MapView request: '%s' Mapviewdata: %s" % (requesttype, layerdata))

            if requesttype == 'subscribe':
                # TODO: Verify everything and send a response
                if layeruuid in self._subscribers:
                    self._subscribers[layeruuid].append(useruuid)
                else:
                    self._subscribers[layeruuid] = [useruuid]
                return
            elif requesttype == 'unsubscribe':
                # TODO: Verify everything and send a response
                self._subscribers[layeruuid].remove(useruuid)
                if len(self._subscribers[layeruuid]) == 0:
                    del (self._subscribers[layeruuid])
                return
            elif requesttype == 'update':
                dblayer = None
                hfoslog("[LM] Update begin")
                try:
                    dblayer = layerobject.find_one({'uuid': useruuid})

                    dblayer.update(layerdata)
                    dblayer.save()
                    hfoslog("[LM] Valid update stored.")
                except Exception as e:
                    hfoslog("[LM] Database layer not available. Looked for '%s' got error: '%s' (%s)" % (
                        useruuid, e, type(e)))

                if not dblayer:
                    try:
                        hfoslog("[LM] New MapView: ", layerdata)
                        layerdata['uuid'] = useruuid  # make sure
                        dblayer = layerobject(layerdata)
                        dblayer.save()
                        hfoslog("[LM] New MapView stored.")

                        if dblayer.shared:
                            hfoslog("[LM] Broadcasting list update for new layer.")
                            self.fireEvent(broadcast("users", self._generatelayerlist()), "wsserver")
                    except Exception as e:
                        hfoslog("[LM] MapView creation error: '%s' (%s)" % (e, type(e)))
                try:
                    hfoslog("[LM] Subscriptions: ", self._subscribers)
                    hfoslog("[LM] dblayer: ", dblayer._fields)
                    if dblayer.shared:
                        if useruuid in self._subscribers:
                            try:
                                hfoslog("[LM] Broadcasting layer update to subscribers.")
                                layerpacket = {'type': 'layerupdate',
                                               'content': {
                                                   'sender': useruuid,
                                                   'layer': dblayer.serializablefields(),
                                               }
                                               }
                                self._broadcast(layerpacket, dblayer.uuid)
                            except Exception as e:
                                hfoslog("[LM] Transmission error before broadcast: %s" % e)
                        else:
                            hfoslog("[LM] Not subscribed.")

                    else:
                        hfoslog("[LM] Not shared.")
                except Exception as e:
                    hfoslog("[LM] Update error during final layer handling", e)

        except Exception as e:
            hfoslog("[LM] Global Error: '%s' %s" % (e, type(e)), lvl=error)

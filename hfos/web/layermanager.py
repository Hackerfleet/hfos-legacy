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
from hfos.logger import hfoslog, error, verbose, debug, critical


class LayerManager(Component):
    """
    Handles layer updates, subscriptions and broadcasts
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(LayerManager, self).__init__(*args)

        hfoslog("[LM] Started")
        self._subscribers = {}

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

        hfoslog("[LM] Event: ", event, lvl=debug)

        try:
            if event.action == 'list':
                try:
                    dblist = self._generatelayerlist()
                    self.fireEvent(
                        send(event.client.clientuuid, {'component': 'layers', 'action': 'list', 'data': dblist}))
                except Exception as e:
                    hfoslog("[LM] Listing error: ", e, type(e), lvl=error)
                return

        except Exception as e:
            hfoslog("[LM] Global Error: '%s' %s" % (e, type(e)), lvl=error)

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
            hfoslog("[LM] Generated layer list: ", result, lvl=verbose)
            return result
        except Exception as e:
            hfoslog("[LM] Error during list retrieval:", e, type(e), lvl=error)

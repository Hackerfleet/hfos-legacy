"""


Module: Debugger
================

Debugger overlord

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from circuits import Component

from hfos.logger import hfoslog, critical, warn

from uuid import uuid4

import json
try:
    import objgraph
    from guppy import hpy
except ImportError:
    hfoslog("[DBG] Debugger couldn't import objgraph and/or guppy.", lvl=warn)

import inspect

class HFDebugger(Component):
    """
    Debugger manager

    Handles various debug requests.

    """

    channel = "hfosweb"

    def __init__(self, root=None, *args):
        super(HFDebugger, self).__init__(*args)

        if not root:
            from hfos.logger import root
            self.root = root
        else:
            self.root = root
        try:
            self.heapy = hpy()
        except:
            hfoslog("[DBG] Can't use heapy. guppy package missing?")

        hfoslog("[DBG] Started")

    def debugrequest(self, event):
        try:
            hfoslog("[DBG] Event: ", event, lvl=critical)

            if event.action == "storejson":
                hfoslog("[DBG] Storing received object to /tmp", lvl=critical)
                fp = open('/tmp/hfosdebugger_' + str(event.user.useruuid) + "_" + str(uuid4()), "w")
                json.dump(event.data, fp, indent=True)
                fp.close()
            if event.action == "memdebug":
                hfoslog("[DBG] Memory hogs:", lvl=critical)
                objgraph.show_most_common_types(limit=20)
            if event.action == "growth":
                hfoslog("[DBG] Memory growth since last call:", lvl=critical)
                objgraph.show_growth()
            if event.action == "graph":
                objgraph.show_backrefs([self.root], max_depth=42, filename='backref-graph.png')
                hfoslog("[DBG] Backref graph written.", lvl=critical)
            if event.action == "heap":
                hfoslog("[DBG] Heap log:", self.heapy.heap(), lvl=critical)



        except Exception as e:
            hfoslog("[DBG] Exception during debug handling:", e, type(e), lvl=critical)

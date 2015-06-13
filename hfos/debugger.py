"""


Module: Debugger
================

Debugger overlord

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from circuits import Component

from hfos.logger import hfoslog, error, critical

from uuid import uuid4

import json


class HFDebugger(Component):
    """
    Debugger manager

    Handles various debug requests.

    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(HFDebugger, self).__init__(*args)

        hfoslog("DEBUGGER: Started")

    def debugrequest(self, event):
        try:
            hfoslog(event, lvl=critical)

            if event.action == "storejson":
                hfoslog("DBG: Storing received object to /tmp", lvl=critical)
                fp = open('/tmp/hfosdebugger_' + str(event.user.useruuid) + "_" + str(uuid4()), "w")
                json.dump(event.data, fp, indent=True)
                fp.close()
        except Exception as e:
            hfoslog("DBG: Exception during debug handling:", e, type(e), lvl=critical)
"""

Module: Event Recorder
======================

A controllable event recorder utility component

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from time import time
from circuits import handler
from hfos.component import ConfigurableComponent
from hfos.logger import error, warn, hilight

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


class Recorder(ConfigurableComponent):
    """
    Event Recorder

    Handles
    * incoming events, that are recorded to a storable json file
    """

    configprops = {}

    def __init__(self, *args):
        super(Recorder, self).__init__("REC", *args)

        self.log("Started")

    @handler("AuthorizedEvent", channel="*")
    def eventhandler(self, *args):
        self.log("Recording event: ", args, lvl=hilight)
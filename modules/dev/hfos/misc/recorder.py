"""

Module: Event Recorder
======================

A controllable event recorder utility component

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from circuits import handler
from hfos.component import ConfigurableComponent
from hfos.events.system import authorizedevent
from hfos.logger import hilight  # , error, warn
from json import dumps
from time import time

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


class Recorder(ConfigurableComponent):
    """
    Event Recorder

    Handles
    * incoming events, that are recorded to a storable json file
    """

    configprops = {}

    def __init__(self, *args):
        super(Recorder, self).__init__("REC", *args)

        self.logfile = open('/tmp/hfos_recording', 'w')

        self.log("Started")

    @handler()
    def eventhandler(self, event, *args, **kwargs):
        if isinstance(event, authorizedevent):
            self.log("Recording event: ", event, lvl=hilight)

            self.logfile.write(dumps({time(): event}))
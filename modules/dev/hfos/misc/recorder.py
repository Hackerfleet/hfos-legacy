"""

Module: Event Recorder
======================

A controllable event recorder utility component

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import handler
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

        self.active = False

        if self.active:
            self.logfile = open('/tmp/hfos_recording', 'w')

            self.log("Started")

    @handler()
    def eventhandler(self, event, *args, **kwargs):
        if self.active and isinstance(event, authorizedevent):
            self.log("Recording event", lvl=hilight)
            # TODO: The event fields must be serialized to record everything
            #  in order. Component is deactivated until that can be done.
            data = dumps({time(): [event.user.uuid, event.action, event.data]})
            self.logfile.write(data)
            self.logfile.flush()
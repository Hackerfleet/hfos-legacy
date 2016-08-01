"""

Module: Event Playback
======================

A controllable event playback utility component

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from time import time
from hfos.component import ConfigurableComponent
from hfos.logger import error, warn

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


class Playback(ConfigurableComponent):
    """
    Event Playback

    Produces
    * outgoing events, that have previously been recorded to a readable json
    file
    """

    configprops = {}

    def __init__(self, *args):
        super(Playback, self).__init__("PLAY", *args)

        self.log("Started")

"""

Module: Event Playback
======================

A controllable event playback utility component

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent
# from hfos.logger import error, warn
# from time import time

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


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

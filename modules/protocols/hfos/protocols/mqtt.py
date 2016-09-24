"""

Module: MQTTGateway
======================

Doing rather not much except serve as module component entrypoint.

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


class MQTTGateway(ConfigurableComponent):
    """
    Empty hull component to store settings etc.
    """

    configprops = {}

    def __init__(self, **kwargs):
        super(MQTTGateway, self).__init__('MQTT', **kwargs)
        self.log("Started.")
"""


Module BusRepeater
==================

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


class BusRepeater(ConfigurableComponent):
    """
    The BusRepeater component receives new raw sensor data and
    repeates it over configurable tcp/udp/other means.


    """
    channel = "repeater"

    configprops = {}

    def __init__(self, *args):
        """
        Initialize the navigation data component.

        :param args:
        """

        super(BusRepeater, self).__init__('BUSREPEATER', *args)

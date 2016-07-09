"""


Module BusRepeater
==================

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from hfos.component import ConfigurableComponent

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
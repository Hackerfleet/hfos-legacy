"""


Module VesselViewManager
========================

Listens for position broadcasts of all kinds and allows to update
a system generated (Vessel-) MapView accordingly to achieve a moving
map and collision warning functionality.

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""


from hfos.component import ConfigurableComponent

# from hfos.events import send
# from hfos.database import objectmodels  # , ValidationError
# from hfos.events import referenceframe, broadcast, AuthorizedEvents
# from hfos.logger import verbose, critical, warn  # , error

# import json
# from time import time
# import datetime
# from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


class VesselViewManager(ConfigurableComponent):
    """
    The VesselViewManager component receives new navigational data and
    generates or updates vessel data accordingly.


    """
    channel = "navdata"

    configprops = {}

    def __init__(self, *args):
        """
        Initialize the vessel view management component.

        :param args:
        """

        super(VesselViewManager, self).__init__('VESSELMGR', *args)
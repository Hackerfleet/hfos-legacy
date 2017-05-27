"""


Module NavData
==============

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import handler
from hfos.database import objectmodels  # , ValidationError
from hfos.events.objectmanager import updatesubscriptions
from hfos.navdata.events import referenceframe
from hfos.logger import hfoslog, events, debug, verbose, critical, warn, \
    hilight
from hfos.component import ConfigurableComponent
from hfos.events.client import send, broadcast
from uuid import uuid4

from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


class VesselManager(ConfigurableComponent):
    """
    Tracks vessels for navigational and other purposes.
    """
    channel = "navdata"
    configprops = {}

    # TODO: This component uses MapViews and in future, probably other
    # modules' objects, so we need to make sure
    # this fails only with a warning/recommendation to install those other
    # modules instead of a tantrum

    def __init__(self, *args):
        super(VesselManager, self).__init__('VESSEL', *args)

        self.vessel_mapview = None

        self.log('Started')

    def _setup(self):
        sysconfig = objectmodels['systemconfig'].find_one(
            {'active': True})

        try:
            vessel = objectmodels['vessel'].find_one({
                'uuid': sysconfig.vesseluuid
            })
        except AttributeError:
            self.log('No vessel configured in Systemconfig, stopping!',
                     lvl=warn)
            return

        mapview = None

        if hasattr(vessel, 'mapviewuuid'):
            self.log('Found a corresponding mapview: ', vessel.mapviewuuid,
                     lvl=debug)
            mapview = objectmodels['mapview'].find_one(
                {'uuid': vessel.mapviewuuid})

        if mapview is None:
            self.log('Creating a new vessel associated mapview')
            mapview = objectmodels['mapview']({'uuid': str(uuid4())})
            mapview.shared = True
            mapview.name = 'Follow ' + vessel.name
            mapview.description = 'Automatically following mapview for ' + \
                                  vessel.name
            mapview.viewtype = 'vessel'

            self.log('Saving new mapview: ', mapview._fields)
            mapview.save()

            vessel.mapviewuuid = mapview.uuid

            vessel.save()

        self.vessel_mapview = mapview

    @handler('referenceframe', channel='navdata')
    def referenceframeupdate(self, event):
        if self.vessel_mapview is None:
            return

        self.log('Updating system vessel mapview coordinates', event,
                 self.vessel_mapview, lvl=verbose)
        self.log('Data:', event.data, lvl=events)
        frame = event.data['data']

        if 'GLL_lat' in frame and 'GLL_lon' in frame:
            # pprint(frame['GLL_lat'])
            # pprint(self.vesselmapview._fields)
            coords = {
                'lat': float(frame['GLL_lat']),
                'lng': float(frame['GLL_lon']),
                'zoom': 10,
                'autoDiscover': False
            }
            self.vessel_mapview.coords = coords
            self.vessel_mapview.save()

            self.fireEvent(updatesubscriptions(
                uuid=self.vessel_mapview.uuid,
                schema='mapview',
                data=self.vessel_mapview
            ), 'hfosweb')

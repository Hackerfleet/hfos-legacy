"""


Module NavData
==============

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from circuits import Event
from circuits import Timer, handler

from hfos.database import objectmodels  # , ValidationError
from hfos.events.system import AuthorizedEvents, updatesubscriptions
from hfos.navdata.events import referenceframe, navdatarequest
from hfos.logger import hfoslog, events, debug, verbose, critical, warn, \
    hilight
from hfos.component import ConfigurableComponent
from hfos.events.client import send, broadcast
from uuid import uuid4

from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


class NavData(ConfigurableComponent):
    """
    The NavData (Navigation Data) component receives new sensordata and
    generates a new :referenceframe:


    """
    channel = "navdata"

    configprops = {}

    def __init__(self, *args):
        """
        Initialize the navigation data component.

        :param args:
        """

        super(NavData, self).__init__('NAVDATA', *args)

        self.datatypes = {}

        for item in objectmodels['sensordatatype'].find():
            # self.log("Adding sensor datatype to inventory:", item)
            self.datatypes[item.name] = item

        self.log("Added %i sensordatatypes to inventory." % len(
            self.datatypes))

        if len(self.datatypes) == 0:
            self.log("No sensordatatypes found! You may need to install the "
                     "provisions again.", lvl=warn)

        self.sensed = {}

        self.referenceframe = {}  # objectmodels['sensordata']()
        self.referenceages = {}
        self.changed = False

        self.interval = 1
        self.passiveinterval = 10
        self.intervalcount = 0

        self.subscriptions = {}

        AuthorizedEvents['navdata'] = navdatarequest


        Timer(self.interval, Event.create('navdatapush'), self.channel,
              persist=True).register(self)

    @handler('navdatarequest', channel='hfosweb')
    def navdatarequest(self, event):
        if event.action == 'list':
            if event.data == 'sensed':
                packet = {
                    'component': 'navdata',
                    'action': 'list',
                    'data': {
                        'sensed': None
                    }
                }

                sensed = []

                for value in self.sensed.values():
                    sensed.append(value.serializablefields())

                packet['data']['sensed'] = sensed

                self.log("Transmitting list of sensed values:", self.sensed)
                self.fireEvent(send(event.client.uuid, packet), 'hfosweb')
        elif event.action == 'subscribe':
            self.log('Navdata subscription requested for', event.data)

            for item in event.data:
                if item in self.subscriptions:
                    if event.client.uuid not in self.subscriptions[item]:
                        self.subscriptions[item].append(event.client.uuid)
                        self.log("Appended subscription for ", item)
                    else:
                        self.log("Client was already subscribed for that "
                                 "value", lvl=warn)
                else:
                    self.subscriptions[item] = [event.client.uuid]
                    self.log("Created new subscription for ", item)
        elif event.action == 'unsubscribe':
            self.log('Navdata unsubscription requested for', event.data)

            for item in event.data:
                if item in self.subscriptions:
                    if event.client.uuid in self.subscriptions[item]:
                        self.subscriptions[item].remove(event.client.uuid)
                        if len(self.subscriptions[item]) == 0:
                            del self.subscriptions[item]
                            self.log("Removed last subscription for ", item)
                        else:
                            self.log("Removed subscription for ", item)

    @handler('clientdisconnect', channel='hfosweb')
    def clientdisconnect(self, event):
        self.log('Deleting subscriptions for disconnected client', lvl=debug)
        empty = []
        for name, subscription in self.subscriptions.items():
            while event.clientuuid in subscription:
                subscription.remove(event.clientuuid)
            if len(subscription) == 0:
                self.log('Subscription removed. Last subscriber for ',
                         subscription)
                del subscription
                empty.append(name)
        for name in empty:
            self.subscriptions.pop(name)

    def sensordata(self, event):
        """
        Generates a new reference frame from incoming sensordata

        :param event: new sensordata to be merged into referenceframe
        """

        if len(self.datatypes) == 0:
            return

        data = event.data
        timestamp = event.timestamp
        # bus = event.bus

        # TODO: What about multiple busses? That is prepared, but how exactly
        # should they be handled?

        self.log("New incoming navdata:", data, lvl=verbose)

        for name, value in data.items():
            if name in self.datatypes:
                ref = self.datatypes[name]
                self.sensed[name] = ref

                if ref.lastvalue != str(value):
                    # self.log("Reference outdated:", ref._fields)

                    item = {
                        'value': value,
                        'timestamp': timestamp,
                        'type': name
                    }

                    self.referenceframe[name] = value
                    self.referenceages[name] = timestamp

                    # self.log("Subscriptions:", self.subscriptions, ref.name)
                    if ref.name in self.subscriptions:

                        packet = {
                            'component': 'navdata',
                            'action': 'update',
                            'data': item
                        }

                        self.log("Serving update: ", packet, lvl=verbose)
                        for uuid in self.subscriptions[ref.name]:
                            self.log("Serving to ", uuid, lvl=events)
                            self.fireEvent(send(uuid, packet),
                                           'hfosweb')

                    # self.log("New item: ", item)
                    sensordata = objectmodels['sensordata'](item)
                    # self.log("Value entry:", sensordata._fields)

                    if ref.record:
                        self.log("Recording updated reference:",
                                 sensordata._fields)
                        sensordata.save()

                    ref.lastvalue = str(value)
                    ref.timestamp = timestamp
            else:
                self.log("Unknown sensor data received!", data, lvl=warn)

    def navdatapush(self):
        """
        Pushes the current :referenceframe: out to clients.

        :return:
        """

        try:
            self.fireEvent(referenceframe(
                {'data': self.referenceframe, 'ages': self.referenceages}),
                "navdata")
            self.intervalcount += 1

            if self.intervalcount == self.passiveinterval:
                self.fireEvent(broadcast('users', {
                    'component': 'navdata',
                    'action': 'update',
                    'data': {
                        'data': self.referenceframe,
                        'ages': self.referenceages
                    }
                }), "hfosweb")
                self.intervalcount = 0
                # self.log("Reference frame successfully pushed.",
                # lvl=verbose)
        except Exception as e:
            self.log("Could not push referenceframe: ", e, type(e),
                     lvl=critical)


class VesselManager(ConfigurableComponent):
    channel = "navdata"
    configprops = {}

    # TODO: This component uses MapViews and in future, probably other modules' objects, so we need to make sure
    # this fails only with a warning/recommendation to install those other modules instead of a tantrum

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
            #pprint(frame['GLL_lat'])
            #pprint(self.vesselmapview._fields)
            coords = {
                'lat': float(frame['GLL_lat']),
                'lng': float(frame['GLL_lon']),
                'zoom': 10,
                'autoDiscover': False
            }
            self.vessel_mapview.coords = coords
            self.vessel_mapview.save()

            self.fireEvent(updatesubscriptions(uuid=self.vessel_mapview.uuid,
                                               schema='mapview',
                                               data=self.vessel_mapview),
                           'hfosweb')

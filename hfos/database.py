"""


Module: Database
================

Contains the underlying object model manager and generates object factories from Schemata.

Contains
========

userobject: User account factory
profileobject: User profile factory
mapviewobject: Mapview factory

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

import sys

import warmongo

# noinspection PyUnresolvedReferences
from six.moves import input  # noqa - Lazily loaded, may be marked as error, e.g. in IDEs
from hfos.logger import hfoslog, debug, warn, critical
from hfos.schemata import schemastore
from hfos.schemata.profile import Profile
from hfos.schemata.user import User
from hfos.schemata.mapview import MapView
from hfos.schemata.layer import Layer
from hfos.schemata.layergroup import LayerGroup
from hfos.schemata.controllable import Controllable
from hfos.schemata.controller import Controller
from hfos.schemata.client import Clientconfig
from hfos.schemata.wikipage import WikiPage
from hfos.schemata.vessel import VesselSchema
from hfos.schemata.radio import RadioConfig
from hfos.schemata.sensordata import SensorData
from hfos.schemata.dashboard import Dashboard
from hfos.schemata.project import Project

from jsonschema import ValidationError  # NOQA


def clear_all():
    """DANGER!
    *This command is a maintenance tool and clears the complete database.*
    """

    sure = input("Are you sure to drop the complete database content?")
    if not (sure.upper() in ("Y", "J")):
        sys.exit(5)

    import pymongo

    client = pymongo.MongoClient(host="localhost", port=27017)
    db = client["hfos"]

    for col in db.collection_names(include_system_collections=False):
        hfoslog("[DB] Dropping collection ", col, lvl=warn)
        db.drop_collection(col)


warmongo.connect("hfos")


def _buildModelFactories():
    result = {}

    for schemaname in schemastore:

        schema = None

        try:
            schema = schemastore[schemaname]['schema']
        except KeyError:
            hfoslog("[DB] No schema found for ", schemaname, lvl=critical)

        try:
            result[schemaname] = warmongo.model_factory(schema)
        except Exception as e:
            hfoslog("[DB] Could not create factory for schema ", schemaname, schema, lvl=critical)

    return result


def _buildCollections():
    result = {}

    import pymongo
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['hfos']

    for schemaname in schemastore:

        schema = None

        try:
            schema = schemastore[schemaname]['schema']
        except KeyError:
            hfoslog("[DB] No schema found for ", schemaname, lvl=critical)

        try:
            result[schemaname] = db[schemaname]
        except Exception as e:
            hfoslog("[DB] Could not get collection for schema ", schemaname, schema, lvl=critical)

    return result

objectmodels = _buildModelFactories()
collections = _buildCollections()

# TODO: Export the following automatically from the objectmodels?

userobject = warmongo.model_factory(User)
profileobject = warmongo.model_factory(Profile)
clientconfigobject = warmongo.model_factory(Clientconfig)

mapviewobject = warmongo.model_factory(MapView)

layerobject = warmongo.model_factory(Layer)
layergroupobject = warmongo.model_factory(LayerGroup)

controllerobject = warmongo.model_factory(Controller)
controllableobject = warmongo.model_factory(Controllable)

wikipageobject = warmongo.model_factory(WikiPage)

vesselconfigobject = warmongo.model_factory(VesselSchema)
radioconfigobject = warmongo.model_factory(RadioConfig)

projectobject = warmongo.model_factory(Project)

sensordataobject = warmongo.model_factory(SensorData)
dashboardobject = warmongo.model_factory(Dashboard)
from pprint import pprint


def profile(schemaname='sensordata', profiletype='pjs'):
    hfoslog("[SCHEMATA] Profiling ", schemaname)

    schema = schemastore[schemaname]['schema']

    hfoslog("[SCHEMATA] Schema: ", schema, lvl=debug)

    if profiletype == 'warmongo':
        hfoslog("[SCHEMATA] Running Warmongo benchmark")
        testclass = warmongo.model_factory(schema)
    elif profiletype == 'pjs':
        hfoslog("[SCHEMATA] Running PJS benchmark")
        import python_jsonschema_objects as pjs
        hfoslog()
        builder = pjs.ObjectBuilder(schema)
        ns = builder.build_classes()
        pprint(ns)
        testclass = ns[schemaname]
        hfoslog("[SCHEMATA] ns: ", ns, lvl=warn)

    hfoslog("[SCHEMATA] Instantiating 100 elements...")
    for i in range(100):
        testobject = testclass()

    hfoslog("[SCHEMATA] Profiling done")

# profile(schemaname='sensordata', profiletype='warmongo')

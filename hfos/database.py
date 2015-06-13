"""
Hackerfleet Operating System - Backend

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

from six.moves import input  # Lazily loaded, may be marked as error, e.g. in IDEs
from hfos.logger import hfoslog, warn
from hfos.schemata.profile import Profile
from hfos.schemata.user import User
from hfos.schemata.mapview import MapView
from hfos.schemata.layer import Layer
from hfos.schemata.layergroup import LayerGroup
from hfos.schemata.controllable import Controllable
from hfos.schemata.controller import Controller


def clear_all():
    sure = input("Are you sure to drop the complete database content?")
    if not (sure.upper() in ("Y", "J")):
        sys.exit(5)

    import pymongo

    client = pymongo.MongoClient(host="localhost", port=27017)
    db = client["hfos"]

    for col in db.collection_names(include_system_collections=False):
        hfoslog("DB: Dropping collection ", col, lvl=warn)
        db.drop_collection(col)


warmongo.connect("hfos")

# TODO: This could be automated via the schemata-store. Hmm.

userobject = warmongo.model_factory(User)
profileobject = warmongo.model_factory(Profile)

mapviewobject = warmongo.model_factory(MapView)

layerobject = warmongo.model_factory(Layer)
layergroupobject = warmongo.model_factory(LayerGroup)

controllerobject = warmongo.model_factory(Controller)
controllableobject = warmongo.model_factory(Controllable)

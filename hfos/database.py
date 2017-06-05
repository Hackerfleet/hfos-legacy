#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2017 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "GPLv3"

"""


Module: Database
================

Contains the underlying object model manager and generates object factories
from Schemata.

Contains
========

Schemastore and Objectstore builder functions.


"""

import sys
import warmongo
import pymongo
# noinspection PyUnresolvedReferences
from six.moves import \
    input  # noqa - Lazily loaded, may be marked as error, e.g. in IDEs
from hfos.logger import hfoslog, debug, warn, critical, verbose
from jsonschema import ValidationError  # NOQA
from pkg_resources import iter_entry_points, DistributionNotFound
from pprint import pprint
from random import choice

schemastore = None
configschemastore = {}
objectmodels = None
collections = None


def makesalt():
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars = []
    for i in range(16):
        chars.append(choice(alphabet))

    return "".join(chars)


def clear_all():
    """DANGER!
    *This command is a maintenance tool and clears the complete database.*
    """

    sure = input("Are you sure to drop the complete database content?")
    if not (sure.upper() in ("Y", "J")):
        sys.exit(5)

    # TODO: Accept argument for dbhost
    client = pymongo.MongoClient(host="localhost", port=27017)
    db = client["hfos"]

    for col in db.collection_names(include_system_collections=False):
        hfoslog("Dropping collection ", col, lvl=warn, emitter='DB')
        db.drop_collection(col)


def _build_schemastore_new():
    available = {}

    for schema_entrypoint in iter_entry_points(group='hfos.schemata',
                                               name=None):
        try:
            hfoslog("Schemata found: ", schema_entrypoint.name, lvl=verbose,
                    emitter='DB')

            available[schema_entrypoint.name] = schema_entrypoint.load()
        except (ImportError, DistributionNotFound) as e:
            hfoslog("Problematic schema: ", e, type(e),
                    schema_entrypoint.name, exc=True, lvl=warn,
                    emitter='SCHEMATA')

    hfoslog("Found schemata: ", sorted(available.keys()), lvl=debug,
            emitter='SCHEMATA')
    # pprint(available)

    return available


def _build_model_factories(store):
    result = {}

    for schemaname in store:

        schema = None

        try:
            schema = store[schemaname]['schema']
        except KeyError:
            hfoslog("No schema found for ", schemaname, lvl=critical,
                    emitter='DB')

        try:
            result[schemaname] = warmongo.model_factory(schema)
        except Exception as e:
            hfoslog("Could not create factory for schema ", e, type(e),
                    schemaname, schema,
                    lvl=critical, emitter='DB')

    return result


def _build_collections(store):
    result = {}

    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['hfos']

    for schemaname in store:

        schema = None

        try:
            schema = store[schemaname]['schema']
        except KeyError:
            hfoslog("No schema found for ", schemaname, lvl=critical,
                    emitter='DB')

        try:
            result[schemaname] = db[schemaname]
        except Exception as e:
            hfoslog("Could not get collection for schema ", schemaname, schema,
                    e, lvl=critical, emitter='DB')

    return result


def initialize(address='127.0.0.1:27017', database_name='hfos'):
    global schemastore
    global objectmodels
    global collections

    hfoslog("Testing database availability to ", address, lvl=debug,
            emitter='DB')

    try:
        client = pymongo.MongoClient(host=address.split(":")[0], port=int(
            address.split(":")[1]) if ":" in address else 27017)
        db = client[database_name]
        hfoslog("Database: ", db.command('buildinfo'), lvl=debug, emitter='DB')
    except Exception as e:
        hfoslog("No database available! Check if you have mongodb > 3.0 "
                "installed and running as well as listening on port 27017 "
                "of localhost. (Error: %s) -> EXIT" % e, lvl=critical,
                emitter='DB')
        sys.exit(5)

    warmongo.connect(database_name)

    schemastore = _build_schemastore_new()
    objectmodels = _build_model_factories(schemastore)
    collections = _build_collections(schemastore)


def test_schemata():
    objects = {}

    for schemaname in schemastore.keys():
        objects[schemaname] = warmongo.model_factory(
            schemastore[schemaname]['schema'])
        try:
            testobject = objects[schemaname]()
            testobject.validate()
        except Exception as e:
            hfoslog('Blank schema did not validate:', schemaname, e,
                    type(e), lvl=verbose, emitter='DB')

    pprint(objects)


def profile(schemaname='sensordata', profiletype='pjs'):
    hfoslog("Profiling ", schemaname, emitter='DB')

    schema = schemastore[schemaname]['schema']

    hfoslog("Schema: ", schema, lvl=debug, emitter='DB')

    testclass = None

    if profiletype == 'warmongo':
        hfoslog("Running Warmongo benchmark", emitter='DB')
        testclass = warmongo.model_factory(schema)
    elif profiletype == 'pjs':
        hfoslog("Running PJS benchmark", emitter='DB')
        try:
            import python_jsonschema_objects as pjs
        except ImportError:
            hfoslog("PJS benchmark selected but not available. Install "
                    "python_jsonschema_objects (PJS)", emitter="DB")
        hfoslog()
        builder = pjs.ObjectBuilder(schema)
        ns = builder.build_classes()
        pprint(ns)
        testclass = ns[schemaname]
        hfoslog("ns: ", ns, lvl=warn, emitter='DB')

    if testclass is not None:
        hfoslog("Instantiating elements...", emitter='DB')
        for i in range(100):
            testclass()
    else:
        hfoslog("No Profiletype available!", emitter="DB")

    hfoslog("Profiling done", emitter='DB')

# profile(schemaname='sensordata', profiletype='warmongo')

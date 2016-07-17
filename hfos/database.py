"""


Module: Database
================

Contains the underlying object model manager and generates object factories
from Schemata.

Contains
========

Schemastore and Objectstore builder functions.

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

import sys
import warmongo
# noinspection PyUnresolvedReferences
from six.moves import \
    input  # noqa - Lazily loaded, may be marked as error, e.g. in IDEs
from hfos.logger import hfoslog, debug, warn, critical, verbose
from jsonschema import ValidationError  # NOQA
from pkg_resources import iter_entry_points
from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

warmongo.connect("hfos")

schemastore = None
objectmodels = None
collections = None


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
        hfoslog("Dropping collection ", col, lvl=warn, emitter='DB')
        db.drop_collection(col)


def _build_schemastore_new():
    available_schemata = {}

    for schema_entrypoint in iter_entry_points(group='hfos.schemata',
                                               name=None):
        hfoslog("Schemata found: ", schema_entrypoint.name, lvl=debug,
                emitter='DB')
        try:
            available_schemata[
                schema_entrypoint.name] = schema_entrypoint.load()
        except ImportError as e:
            hfoslog("Problematic schema: ", e, type(e),
                    schema_entrypoint.name, exc=True, lvl=warn,
                    emitter='SCHEMATA')

    hfoslog("Found schemata: ", available_schemata.keys(),
            emitter='SCHEMATA')
    # pprint(available_schemata)

    return available_schemata


def _build_model_factories():
    global schemastore

    result = {}

    for schemaname in schemastore:

        schema = None

        try:
            schema = schemastore[schemaname]['schema']
        except KeyError:
            hfoslog("No schema found for ", schemaname, lvl=critical,
                    emitter='DB')

        try:
            result[schemaname] = warmongo.model_factory(schema)
        except Exception as e:
            hfoslog("Could not create factory for schema ", schemaname, schema,
                    lvl=critical, emitter='DB')

    return result


def _build_collections():
    global schemastore

    result = {}

    import pymongo
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['hfos']

    for schemaname in schemastore:

        schema = None

        try:
            schema = schemastore[schemaname]['schema']
        except KeyError:
            hfoslog("No schema found for ", schemaname, lvl=critical,
                    emitter='DB')

        try:
            result[schemaname] = db[schemaname]
        except Exception as e:
            hfoslog("Could not get collection for schema ", schemaname, schema,
                    lvl=critical, emitter='DB')

    return result


def initialize():
    global schemastore
    global objectmodels
    global collections

    schemastore = _build_schemastore_new()
    objectmodels = _build_model_factories()
    collections = _build_collections()


def test_schemata():
    objects = {}

    for schemaname, meta in schemastore.items():
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
    from pprint import pprint
    hfoslog("Profiling ", schemaname, emitter='DB')

    schema = schemastore[schemaname]['schema']

    hfoslog("Schema: ", schema, lvl=debug, emitter='DB')

    if profiletype == 'warmongo':
        hfoslog("Running Warmongo benchmark", emitter='DB')
        testclass = warmongo.model_factory(schema)
    elif profiletype == 'pjs':
        hfoslog("Running PJS benchmark", emitter='DB')
        import python_jsonschema_objects as pjs
        hfoslog()
        builder = pjs.ObjectBuilder(schema)
        ns = builder.build_classes()
        pprint(ns)
        testclass = ns[schemaname]
        hfoslog("ns: ", ns, lvl=warn, emitter='DB')

    hfoslog("Instantiating 100 elements...", emitter='DB')
    for i in range(100):
        testobject = testclass()

    hfoslog("Profiling done", emitter='DB')

# profile(schemaname='sensordata', profiletype='warmongo')

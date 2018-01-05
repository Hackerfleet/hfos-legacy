#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2018 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

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
import operator
from os import statvfs, walk
from os.path import join, getsize
# noinspection PyUnresolvedReferences
from six.moves import \
    input  # noqa - Lazily loaded, may be marked as error, e.g. in IDEs
from circuits import Timer, Event
from hfos.logger import hfoslog, debug, warn, error, critical, verbose
from hfos.component import ConfigurableComponent, handler
from jsonschema import ValidationError  # NOQA
from pkg_resources import iter_entry_points, DistributionNotFound
from pprint import pprint
from random import choice

try:  # 2/3
    PermissionError
except NameError:
    PermissionError = IOError  # NOQA

schemastore = None
configschemastore = {}
objectmodels = None
collections = None


def makesalt():
    """Generates a cryptographically sane salt of 16 alphanumeric characters"""

    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars = []
    for i in range(16):
        chars.append(choice(alphabet))

    return "".join(chars)


def clear_all():
    """DANGER!
    *This command is a maintenance tool and clears the complete database.*
    """

    sure = input("Are you sure to drop the complete database content? (Type "
                 "in upppercase YES)")
    if not (sure == 'YES'):
        hfoslog('Not deleting the database.')
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
            schema = schema_entrypoint.load()
            available[schema_entrypoint.name] = schema
        except (ImportError, DistributionNotFound) as e:
            hfoslog("Problematic schema: ", e, type(e),
                    schema_entrypoint.name, exc=True, lvl=warn,
                    emitter='SCHEMATA')

    hfoslog("Found", len(available), "schemata: ", sorted(available.keys()),
            lvl=debug,
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
    """Initializes the database connectivity, schemata and finally
    object models"""

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
    """Validates all registered schemata"""

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
    """Profiles object model handling with a very simple benchmarking test"""

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
            return

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

class Maintenance(ConfigurableComponent):
    """Regularly checks a few basic system maintenance tests like used
    storage space of collections and other data"""

    configprops = {
        'locations': {
            'type': 'object',
            'properties': {
                'cache': {
                    'type': 'object',
                    'properties': {
                        'minimum': {
                            'type': 'integer',
                            'description': 'Minimum cache free space to '
                                           'alert on',
                            'title': 'Minimum cache',
                            'default': 500 * 1024 * 1024
                        },
                        'location': {
                            'type': 'string',
                            'description': 'Location of cache data',
                            'title': 'Cache location',
                            'default': '/var/cache/hfos'
                        }
                    },
                    'default': {}
                },
                'library': {
                    'type': 'object',
                    'properties': {
                        'minimum': {
                            'type': 'integer',
                            'description': 'Minimum library free space to '
                                           'alert on',
                            'title': 'Minimum library space',
                            'default': 50 * 1024 * 1024
                        },
                        'location': {
                            'type': 'string',
                            'description': 'Location of library data',
                            'title': 'Library location',
                            'default': '/var/lib/hfos'
                        }
                    },
                    'default': {}
                }
            },
            'default': {}
        },
        'interval': {
            'type': 'integer',
            'title': 'Check interval',
            'description': 'Interval in seconds to check maintenance '
                           'conditions',
            'default': 43200
        }
    }

    def __init__(self, *args, **kwargs):
        super(Maintenance, self).__init__("MAINTENANCE", *args, **kwargs)
        self.log("Maintenance started")

        # TODO: Accept argument for dbhost
        client = pymongo.MongoClient(host="localhost", port=27017)
        self.db = client["hfos"]

        self.collection_sizes = {}
        self.collection_total = 0

        self.disk_allocated = {}
        self.disk_free = {}

        self.maintenance_check()
        self.timer = Timer(
            self.config.interval,
            Event.create('maintenance_check'), persist=True
        ).register(self)

    @handler('maintenance_check')
    def maintenance_check(self, *args):
        """Perform a regular maintenance check"""

        self.log('Performing maintenance check')
        self._check_collections()
        self._check_free_space()

    def _check_collections(self):
        """Checks node local collection storage sizes"""

        self.collection_sizes = {}
        self.collection_total = 0
        for col in self.db.collection_names(include_system_collections=False):
            self.collection_sizes[col] = self.db.command('collstats', col).get(
                'storageSize', 0)
            self.collection_total += self.collection_sizes[col]

        sorted_x = sorted(self.collection_sizes.items(),
                          key=operator.itemgetter(1))

        for item in sorted_x:
            self.log("Collection size (%s): %.2f MB" % (
                item[0], item[1] / 1024.0 / 1024),
                     lvl=verbose)

        self.log("Total collection sizes: %.2f MB" % (self.collection_total /
                                                      1024.0 / 1024))

    def _check_free_space(self):
        """Checks used filesystem storage sizes"""

        def get_folder_size(path):
            """Aggregates used size of a specified path, recursively"""

            total_size = 0
            for item in walk(path):
                for file in item[2]:
                    try:
                        total_size = total_size + getsize(join(item[0], file))
                    except (OSError, PermissionError) as e:
                        self.log("error with file:  " + join(item[0], file), e)
            return total_size

        for name, checkpoint in self.config.locations.items():
            try:
                stats = statvfs(checkpoint['location'])
            except (OSError, PermissionError) as e:
                self.log('Location unavailable:', name, e, type(e),
                         lvl=error, exc=True)
                continue
            free_space = stats.f_frsize * stats.f_bavail
            used_space = get_folder_size(
                checkpoint['location']
            ) / 1024.0 / 1024

            self.log('Location %s uses %.2f MB' % (name, used_space))

            if free_space < checkpoint['minimum']:
                self.log('Short of free space on %s: %.2f MB left' % (
                    name, free_space / 1024.0 / 1024 / 1024),
                         lvl=warn)

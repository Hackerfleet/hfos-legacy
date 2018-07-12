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
from hfos.misc import all_languages

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
import time
import json
import jsonschema
from copy import deepcopy
from jsonschema import ValidationError  # NOQA
from ast import literal_eval
from pprint import pprint

import operator
import pymongo
import warmongo
from circuits import Timer, Event
from os import statvfs, walk
from os.path import join, getsize
from pkg_resources import iter_entry_points, DistributionNotFound
# noinspection PyUnresolvedReferences
from six.moves import \
    input  # noqa - Lazily loaded, may be marked as error, e.g. in IDEs

from hfos.component import ConfigurableComponent, handler
from hfos.logger import hfoslog, debug, warn, error, critical, verbose
from hfos.misc import i18n as _


def db_log(*args, **kwargs):
    kwargs.update({'emitter': 'DB', 'frame_ref': 2})
    hfoslog(*args, **kwargs)


def backup_log(*args, **kwargs):
    kwargs.update({'emitter': 'BACKUP', 'frame_ref': 2})
    hfoslog(*args, **kwargs)


def schemata_log(*args, **kwargs):
    kwargs.update({'emitter': 'SCHEMATA', 'frame_ref': 2})
    hfoslog(*args, **kwargs)


try:  # PY 2/3
    PermissionError
except NameError:
    PermissionError = IOError  # NOQA

schemastore = None
l10n_schemastore = {}
configschemastore = {}
objectmodels = None
collections = None
dbhost = ""
dbport = 0
dbname = ""
instance = ""
initialized = False

# Necessary against import de-optimizations
ValidationError = ValidationError


def clear_all():
    """DANGER!
    *This command is a maintenance tool and clears the complete database.*
    """

    sure = input("Are you sure to drop the complete database content? (Type "
                 "in upppercase YES)")
    if not (sure == 'YES'):
        db_log('Not deleting the database.')
        sys.exit(5)

    client = pymongo.MongoClient(host=dbhost, port=dbport)
    db = client[dbname]

    for col in db.collection_names(include_system_collections=False):
        db_log("Dropping collection ", col, lvl=warn)
        db.drop_collection(col)


def _build_schemastore_new():
    available = {}

    for schema_entrypoint in iter_entry_points(group='hfos.schemata',
                                               name=None):
        try:
            schemata_log("Schemata found: ", schema_entrypoint.name, lvl=verbose)
            schema = schema_entrypoint.load()
            available[schema_entrypoint.name] = schema
        except (ImportError, DistributionNotFound) as e:
            schemata_log("Problematic schema: ", schema_entrypoint.name, exc=True, lvl=warn)

    def schema_insert(dictionary, path, obj):
        path = path.split('/')

        place = dictionary

        for element in path:
            if element != '':
                place = place[element]

        place.update(obj)

        return dictionary

    def form_insert(form, index, path, obj):
        path = path.split('/')

        if isinstance(index, str):
            for widget in form:
                if isinstance(widget, dict) and widget.get('id', None) is not None:
                    place = widget
        else:
            place = form[index]

        for element in path:
            schemata_log(element, place, lvl=verbose)
            try:
                element = int(element)
            except ValueError:
                pass
            if element != '':
                place = place[element]

        if isinstance(place, dict):
            place.update(obj)
        else:
            place.append(obj)

        return form

    for key, item in available.items():
        extends = item.get('extends', None)
        if extends is not None:
            schemata_log(key, 'extends:', extends, pretty=True, lvl=verbose)

            for model, extension_group in extends.items():
                schema_extensions = extension_group.get('schema', None)
                form_extensions = extension_group.get('form', None)
                schema = available[model].get('schema', None)
                form = available[model].get('form', None)

                original_schema = deepcopy(schema)

                if schema_extensions is not None:
                    schemata_log('Extending schema', model, 'from', key, lvl=debug)
                    for path, extensions in schema_extensions.items():
                        schemata_log('Item:', path, 'Extensions:', extensions, lvl=verbose)
                        for obj in extensions:
                            available[model]['schema'] = schema_insert(schema, path, obj)
                            schemata_log('Path:', path, 'obj:', obj, lvl=verbose)

                if form_extensions is not None:
                    schemata_log('Extending form of', model, 'with', key, lvl=verbose)
                    for index, extensions in form_extensions.items():
                        schemata_log('Item:', index, 'Extensions:', extensions, lvl=verbose)
                        for path, obj in extensions.items():
                            available[model]['form'] = form_insert(form, index, path, obj)
                            schemata_log('Path:', path, 'obj:', obj, lvl=verbose)

                # schemata_log(available[model]['form'], pretty=True, lvl=warn)
                try:
                    jsonschema.Draft4Validator.check_schema(schema)
                except jsonschema.SchemaError as e:
                    schemata_log('Schema extension failed:', model, extension_group, exc=True)
                    available[model]['schema'] = original_schema

    schemata_log("Found", len(available), "schemata: ", sorted(available.keys()), lvl=debug)

    return available


def _build_l10n_schemastore(available):
    l10n_schemata = {}

    for lang in all_languages():

        language_schemata = {}

        def translate(schema):
            """Generate a translated copy of a schema"""

            localized = deepcopy(schema)

            def walk(branch):
                """Inspect a schema recursively to translate descriptions and titles"""

                if isinstance(branch, dict):

                    if 'title' in branch and isinstance(branch['title'], str):
                        # schemata_log(branch['title'])
                        branch['title'] = _(branch['title'], lang=lang)
                    if 'description' in branch and isinstance(branch['description'], str):
                        # schemata_log(branch['description'])
                        branch['description'] = _(branch['description'], lang=lang)

                    for key, item in branch.items():
                        walk(item)

            walk(localized)

            return localized

        for key, item in available.items():
            language_schemata[key] = translate(item)

        l10n_schemata[lang] = language_schemata

        # schemata_log(l10n_schemata['de']['client'], pretty=True, lvl=error)

    return l10n_schemata


def _build_model_factories(store):
    """Generate factories to construct objects from schemata"""

    result = {}

    for schemaname in store:

        schema = None

        try:
            schema = store[schemaname]['schema']
        except KeyError:
            schemata_log("No schema found for ", schemaname, lvl=critical, exc=True)

        try:
            result[schemaname] = warmongo.model_factory(schema)
        except Exception as e:
            schemata_log("Could not create factory for schema ", schemaname, schema, lvl=critical, exc=True)

    return result


def _build_collections(store):
    """Generate database collections with indices from the schemastore"""

    result = {}

    client = pymongo.MongoClient(host=dbhost, port=dbport)
    db = client[dbname]

    for schemaname in store:

        schema = None
        indices = None

        try:
            schema = store[schemaname]['schema']
            indices = store[schemaname].get('indices', None)
        except KeyError:
            db_log("No schema found for ", schemaname, lvl=critical)

        try:
            result[schemaname] = db[schemaname]
        except Exception:
            db_log("Could not get collection for schema ", schemaname, schema, lvl=critical, exc=True)

        if indices is not None:
            col = db[schemaname]
            db_log('Adding indices to', schemaname, lvl=debug)
            i = 0
            keys = list(indices.keys())

            while i < len(indices):
                index_name = keys[i]
                index = indices[index_name]

                index_type = index.get('type', None)
                index_unique = index.get('unique', False)
                index_sparse = index.get('sparse', True)
                index_reindex = index.get('reindex', False)

                if index_type in (None, 'text'):
                    index_type = pymongo.TEXT
                elif index_type == '2dsphere':
                    index_type = pymongo.GEOSPHERE

                def do_index():
                    col.ensure_index([(index_name, index_type)],
                                     unique=index_unique,
                                     sparse=index_sparse)

                db_log('Enabling index of type', index_type, 'on', index_name, lvl=debug)
                try:
                    do_index()
                    i += 1
                except pymongo.errors.OperationFailure:
                    db_log(col.list_indexes().__dict__, pretty=True, lvl=verbose)
                    if not index_reindex:
                        db_log('Index was not created!', lvl=warn)
                        i += 1
                    else:
                        try:
                            col.drop_index(index_name)
                            do_index()
                            i += 1
                        except pymongo.errors.OperationFailure as e:
                            db_log('Index recreation problem:', exc=True, lvl=error)
                            col.drop_indexes()
                            i = 0

                            # for index in col.list_indexes():
                            #    db_log("Index: ", index)
    return result


def initialize(address='127.0.0.1:27017', database_name='hfos', instance_name="default", reload=False):
    """Initializes the database connectivity, schemata and finally object models"""

    global schemastore
    global l10n_schemastore
    global objectmodels
    global collections
    global dbhost
    global dbport
    global dbname
    global instance
    global initialized

    if initialized and not reload:
        hfoslog('Already initialized and not reloading.', lvl=warn, emitter="DB", frame_ref=2)
        return

    dbhost = address.split(':')[0]
    dbport = int(address.split(":")[1]) if ":" in address else 27017
    dbname = database_name

    db_log("Using database:", dbname, '@', dbhost, ':', dbport)

    try:
        client = pymongo.MongoClient(host=dbhost, port=dbport)
        db = client[dbname]
        db_log("Database: ", db.command('buildinfo'), lvl=debug)
    except Exception as e:
        db_log("No database available! Check if you have mongodb > 3.0 "
               "installed and running as well as listening on port 27017 "
               "of localhost. (Error: %s) -> EXIT" % e, lvl=critical)
        sys.exit(5)

    warmongo.connect(database_name)

    schemastore = _build_schemastore_new()
    l10n_schemastore = _build_l10n_schemastore(schemastore)
    objectmodels = _build_model_factories(schemastore)
    collections = _build_collections(schemastore)
    instance = instance_name
    initialized = True


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
            db_log('Blank schema did not validate:', schemaname, exc=True)

            # pprint(objects)


def profile(schemaname='sensordata', profiletype='pjs'):
    """Profiles object model handling with a very simple benchmarking test"""

    db_log("Profiling ", schemaname)

    schema = schemastore[schemaname]['schema']

    db_log("Schema: ", schema, lvl=debug)

    testclass = None

    if profiletype == 'warmongo':
        db_log("Running Warmongo benchmark")
        testclass = warmongo.model_factory(schema)
    elif profiletype == 'pjs':
        db_log("Running PJS benchmark")
        try:
            import python_jsonschema_objects as pjs
        except ImportError:
            db_log("PJS benchmark selected but not available. Install "
                   "python_jsonschema_objects (PJS)")
            return

        db_log()
        builder = pjs.ObjectBuilder(schema)
        ns = builder.build_classes()
        pprint(ns)
        testclass = ns[schemaname]
        db_log("ns: ", ns, lvl=warn)

    if testclass is not None:
        db_log("Instantiating elements...")
        for i in range(100):
            testclass()
    else:
        db_log("No Profiletype available!")

    db_log("Profiling done")


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
                            'default': join('/var/cache/hfos', instance)
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
                            'default': join('/var/lib/hfos', instance)
                        }
                    },
                    'default': {}
                },
                'backup': {
                    'type': 'object',
                    'properties': {
                        'minimum': {
                            'type': 'integer',
                            'description': 'Minimum backup free space to '
                                           'alert on',
                            'title': 'Minimum backup space',
                            'default': 50 * 1024 * 1024
                        },
                        'location': {
                            'type': 'string',
                            'description': 'Location of backup data',
                            'title': 'Backup location',
                            'default': join('/var/local/hfos/', instance, 'backup')
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

        client = pymongo.MongoClient(dbhost, dbport)
        self.db = client[dbname]

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


class BackupManager(ConfigurableComponent):
    """Regularly creates backups of collections"""

    configprops = {
        'location': {
            'type': 'string',
            'description': 'Location of library data',
            'title': 'Library location',
            'default': join('/var/local/hfos', instance, 'backup')
        },
        'interval': {
            'type': 'integer',
            'title': 'Backup interval',
            'description': 'Interval in seconds to create Backup',
            'default': 86400
        }
    }

    def __init__(self, *args, **kwargs):
        super(BackupManager, self).__init__("BACKUP", *args, **kwargs)
        self.log("Backup manager started")

        self.timer = Timer(
            self.config.interval,
            Event.create('backup'), persist=True
        ).register(self)

    @handler('backup')
    def backup(self, *args):
        """Perform a regular backup"""

        self.log('Performing backup')
        self._create_backup()

    def _create_backup(self):
        self.log('Backing up all data')

        filename = time.strftime("%Y-%m-%d_%H%M%S.json")
        filename = join(self.config.location, filename)

        backup(None, None, None, 'json', filename, False, True, [])


def backup(schema, uuid, export_filter, export_format, filename, pretty, export_all, omit):
    """Exports all collections to (JSON-) files."""

    export_format = export_format.upper()

    if pretty:
        indent = 4
    else:
        indent = 0

    f = None

    if filename:
        try:
            f = open(filename, 'w')
        except (IOError, PermissionError) as e:
            backup_log('Could not open output file for writing:', exc=True, lvl=error)
            return

    def output(what, convert=False):
        """Output the backup in a specified format."""

        if convert:
            if export_format == 'JSON':
                data = json.dumps(what, indent=indent)
            else:
                data = ""
        else:
            data = what

        if not filename:
            print(data)
        else:
            f.write(data)

    if schema is None:
        if export_all is False:
            backup_log('No schema given.', lvl=warn)
            return
        else:
            schemata = objectmodels.keys()
    else:
        schemata = [schema]

    all_items = {}

    for schema_item in schemata:
        model = objectmodels[schema_item]

        if uuid:
            obj = model.find({'uuid': uuid})
        elif export_filter:
            obj = model.find(literal_eval(export_filter))
        else:
            obj = model.find()

        items = []
        for item in obj:
            fields = item.serializablefields()
            for field in omit:
                try:
                    fields.pop(field)
                except KeyError:
                    pass
            items.append(fields)

        all_items[schema_item] = items

        # if pretty is True:
        #    output('\n// Objectmodel: ' + schema_item + '\n\n')
        # output(schema_item + ' = [\n')

    output(all_items, convert=True)

    if f is not None:
        f.flush()
        f.close()

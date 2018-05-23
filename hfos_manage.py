#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System - Dev Plugin
# =================================================
# Copyright (C) 2011-2016 riot <riot@c-base.org> and others.
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

from __future__ import print_function

import bson
import deepdiff

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""

HFOS Management Tool
====================

This is the management tool utility to install, configure and maintain
Hackerfleet Operating System installations.

"""

import click
import getpass
import grp
import hashlib
import json
import os
import sys
import shutil
import pwd
import pymongo
import time

from click_plugins import with_plugins
from click_didyoumean import DYMGroup
from click_repl import repl
from prompt_toolkit.history import FileHistory

from pkg_resources import iter_entry_points
from ast import literal_eval
from distutils.dir_util import copy_tree
from uuid import uuid4
from collections import OrderedDict
from OpenSSL import crypto
from socket import gethostname
from pprint import pprint
from warmongo import model_factory
from pymongo.errors import DuplicateKeyError

from hfos.ui.builder import install_frontend
from hfos.migration import make_migrations
from hfos.logger import debug, warn, error, verbosity, hfoslog
from hfos.tools import write_template_file
from hfos.database import backup

# 2.x/3.x imports: (TODO: Simplify those, one 2x/3x ought to be enough)
try:
    # noinspection PyUnresolvedReferences
    input = raw_input  # NOQA
except NameError:
    pass

try:
    from subprocess import Popen, PIPE
except ImportError:
    # noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
    from subprocess32 import Popen, PIPE  # NOQA

try:
    # noinspection PyUnresolvedReferences
    unicode  # NOQA
except NameError:
    unicode = str

distribution = 'DEBIAN'

service_template = 'hfos.service'
nginx_configuration = 'nginx.conf'

key_file = "/etc/ssl/certs/hfos/selfsigned.key"
cert_file = "/etc/ssl/certs/hfos/selfsigned.crt"
combined_file = "/etc/ssl/certs/hfos/selfsigned.pem"

paths = [
    'hfos',
    'hfos/{plugin_name}',
    'hfos-frontend/{plugin_name}/scripts/controllers',
    'hfos-frontend/{plugin_name}/views'
]

templates = {
    'setup_file': ('setup.py.template', 'setup.py'),
    'package_file': ('package.json.template', 'package.json'),
    'component': (
        'component.py.template', 'hfos/{plugin_name}/{plugin_name}.py'),
    'module_init': ('init.py.template', 'hfos/__init__.py'),
    'package_init': ('init.py.template', 'hfos/{plugin_name}/__init__.py'),
    'schemata': ('schemata.py.template', 'hfos/{plugin_name}/schemata.py'),
    'controller': ('controller.js.template',
                   'hfos-frontend/{plugin_name}/scripts/controllers/{'
                   'plugin_name}.js'),
    'view': (
        'view.html.template',
        'hfos-frontend/{plugin_name}/views/{plugin_name}.html')
}

questions = OrderedDict({
    'plugin_name': 'plugin',
    'author_name': u'author',
    'author_email': u'author@domain.tld',
    'description': u'Description',
    'long_description': u'Very long description, use \\n to get multilines.',
    'version': '0.0.1',
    'github_url': 'hackerfleet/example',
    'license': 'GPLv3',
    'keywords': 'hfos example plugin'

})

info_header = """The manage command guides you through setting up a new HFOS
package.
It provides basic setup. If you need dependencies or have other special
needs, edit the resulting files by hand.

You can press Ctrl-C any time to cancel this process.

See hfos_manage --help for more details.
"""


def log(*args, **kwargs):
    """Log as Emitter:MANAGE"""

    kwargs.update({'emitter': 'MANAGE'})
    hfoslog(*args, **kwargs)


def _check_root():
    """Check if current user has root permissions"""

    if os.geteuid() != 0:
        log("Need root access to install. Use sudo!", lvl=error)
        log("If you installed into a virtual environment, don't forget to "
            "specify the interpreter binary for sudo, e.g:\n"
            "$ sudo /home/user/.virtualenv/hfos/bin/python3 "
            "hfos_manage.py")

        sys.exit(1)


def _augment_info(info):
    """Fill out the template information"""

    info['description_header'] = "=" * len(info['description'])
    info['component_name'] = info['plugin_name'].capitalize()
    info['year'] = time.localtime().tm_year
    info['license_longtext'] = ''

    info['keyword_list'] = u""
    for keyword in info['keywords'].split(" "):
        print(keyword)
        info['keyword_list'] += u"\'" + str(keyword) + u"\', "
    print(info['keyword_list'])
    if len(info['keyword_list']) > 0:
        # strip last comma
        info['keyword_list'] = info['keyword_list'][:-2]

    return info


def _construct_module(info, target):
    """Build a module from templates and user supplied information"""

    for path in paths:
        real_path = os.path.abspath(os.path.join(target, path.format(**info)))
        log("Making directory '%s'" % real_path)
        os.makedirs(real_path)

    # pprint(info)
    for item in templates.values():
        source = os.path.join('dev/templates', item[0])
        filename = os.path.abspath(
            os.path.join(target, item[1].format(**info)))
        log("Creating file from template '%s'" % filename,
            emitter='MANAGE')
        write_template_file(source, filename, info)


def _ask(question, default=None, data_type='str', show_hint=False):
    """Interactively ask the user for data"""

    data = default

    if data_type == 'bool':
        data = None
        default_string = "Y" if default else "N"

        while data not in ('Y', 'J', 'N', '1', '0'):
            data = input("%s? [%s]: " % (question, default_string)).upper()

            if data == '':
                return default

        return data in ('Y', 'J', '1')

    elif data_type in ('str', 'unicode'):
        if show_hint:
            msg = "%s? [%s] (%s): " % (question, default, data_type)
        else:
            msg = question

        data = input(msg)

        if len(data) == 0:
            data = default
    elif data_type == 'int':
        if show_hint:
            msg = "%s? [%s] (%s): " % (question, default, data_type)
        else:
            msg = question

        data = input(msg)

        if len(data) == 0:
            data = int(default)
        else:
            data = int(data)

    return data


def _ask_questionnaire():
    """Asks questions to fill out a HFOS plugin template"""

    answers = {}
    print(info_header)
    pprint(questions.items())

    for question, default in questions.items():
        response = _ask(question, default, str(type(default)), show_hint=True)
        if type(default) == unicode and type(response) != str:
            response = response.decode('utf-8')
        answers[question] = response

    return answers


def _ask_password():
    """Securely and interactively ask for a password"""

    password = "Foo"
    password_trial = ""

    while password != password_trial:
        password = getpass.getpass()
        password_trial = getpass.getpass(prompt="Repeat:")
        if password != password_trial:
            print("\nPasswords do not match!")

    return password


def _get_credentials(username=None, password=None, dbhost=None):
    """Obtain user credentials by arguments or asking the user"""

    # Database salt
    system_config = dbhost.objectmodels['systemconfig'].find_one({
        'active': True
    })

    try:
        salt = system_config.salt.encode('ascii')
    except (KeyError, AttributeError):
        log('No systemconfig or it is without a salt! '
            'Reinstall the system provisioning with'
            'hfos_manage.py install provisions -p system')
        sys.exit(3)

    if username is None:
        username = _ask("Please enter username: ")
    else:
        username = username

    if password is None:
        password = _ask_password()
    else:
        password = password

    try:
        password = password.encode('utf-8')
    except UnicodeDecodeError:
        password = password

    passhash = hashlib.sha512(password)
    passhash.update(salt)

    return username, passhash.hexdigest()


def _get_system_configuration(dbhost, dbname):
    from hfos import database
    database.initialize(dbhost, dbname)
    systemconfig = database.objectmodels['systemconfig'].find_one({
        'active': True
    })

    return systemconfig

db_host_default = '127.0.0.1:27017'
db_host_help = 'Define hostname for database server (default: ' + \
               db_host_default + ')'
db_host_metavar = '<ip:port>'

db_default = 'hfos'
db_help = 'Define name of database (default: ' + db_default + ')'
db_metavar = '<name>'


@with_plugins(iter_entry_points('hfos.management'))
@click.group(context_settings={'help_option_names': ['-h', '--help']},
             cls=DYMGroup)
@click.option('--instance', default='hfos', help='Name of instance to act on',
              metavar='<name>')
@click.option('--quiet', default=False, help="Suppress all output",
              is_flag=True)
@click.option('--verbose', '-v', default=False, help="Give verbose output",
              is_flag=True)
@click.option('--log', default=20, help='Log level to use (0-100)',
              metavar='<number>')
@click.option('--dbhost', default=db_host_default, help=db_host_help,
              metavar=db_host_metavar)
@click.option('--dbname', default=db_default, help=db_help,
              metavar=db_metavar)
@click.pass_context
def cli(ctx, instance, quiet, verbose, log, dbhost, dbname):
    """HFOS Management Utility

    This utility supports various operations to manage HFOS installations.
    Most of the commands are grouped. To obtain more information about the
    groups' available sub commands/groups, try

    hfos_manage group

    To display details of a command or its sub groups, try

    hfos_manage group [subgroup] [command] --help
    """

    ctx.obj['instance'] = instance
    ctx.obj['quiet'] = quiet
    ctx.obj['verbose'] = verbose
    verbosity['console'] = log
    verbosity['global'] = log

    from hfos import database
    database.initialize(dbhost, dbname)
    ctx.obj['db'] = database
    ctx.obj['dbhost'] = dbhost
    ctx.obj['dbname'] = dbname


@click.command(short_help='create starterkit module')
@click.option('--clear', help='Clears already existing target',
              default=False, is_flag=True)
@click.option("--target", help="Create module in the given folder (uses ./ "
                               "if omitted)", default=".", metavar='<folder>')
def create_module(clear, target):
    """Creates a new template HFOS plugin module"""

    if os.path.exists(target):
        if clear:
            shutil.rmtree(target)
        else:
            log("Target exists! Use --clear to delete it first.",
                emitter='MANAGE')
            sys.exit(2)

    done = False
    info = None

    while not done:
        info = _ask_questionnaire()
        pprint(info)
        done = _ask('Is the above correct', default='y', data_type='bool')

    augmented_info = _augment_info(info)

    log("Constructing module %(plugin_name)s" % info)
    _construct_module(augmented_info, target)



@click.group(cls=DYMGroup)
@click.pass_context
def db(ctx):
    """Database management operations (GROUP)"""


cli.add_command(db)


@db.command(short_help='List all mongodb databases')
@click.pass_context
def list_all(ctx):
    from pymongo import MongoClient

    client = MongoClient(ctx.obj['dbhost'])
    log(client.database_names())
    log('Done')


@db.command(short_help='Rename database')
@click.argument('source')
@click.argument('destination')
@click.option('--keep', is_flag=True, help='Keep original database', default=False)
@click.option('--clear-target', is_flag=True, help='Erase target if it exists', default=False)
@click.pass_context
def rename(ctx, source, destination, keep, clear_target):
    from pymongo import MongoClient

    client = MongoClient(ctx.obj['dbhost'])

    if source not in client.database_names():
        log('Source database', source, 'does not exist!', lvl=warn)
        sys.exit(-1)

    database = client.admin
    log('Copying', source, 'to', destination)

    if destination in client.database_names():
        log('Destination exists')
        if clear_target:
            log('Clearing')
            client.drop_database(destination)
        else:
            log('Not destroying existing data', lvl=warn)
            sys.exit(-1)

    database.command('copydb', fromdb=source, todb=destination)

    if not keep:
        log('Deleting old database')
        client.drop_database(source)

    log('Done')


@db.command(short_help='Irrevocably remove collection content')
@click.argument('schema')
@click.pass_context
def clear(ctx, schema):
    """Clears an entire database collection irrevocably. Use with caution!"""

    response = _ask('Are you sure you want to delete the collection "%s"' % (
        schema), default='N', data_type='bool')
    if response is True:
        host, port = ctx.obj['dbhost'].split(':')

        client = pymongo.MongoClient(host=host, port=int(port))
        db = client[ctx.obj['dbname']]

        log("Clearing collection for", schema, lvl=warn,
            emitter='MANAGE')
        result = db.drop_collection(schema)
        if not result['ok']:
            log("Could not drop collection:", lvl=error)
            log(result, pretty=True, lvl=error)
        else:
            log("Done")


@db.group(cls=DYMGroup)
@click.option("--schema", help="Specify schema to work with",
              default=None)
@click.pass_context
def migrations(ctx, schema):
    """Data migration management (GROUP)"""

    ctx.obj['schema'] = schema


@migrations.command(short_help="make new migrations")
@click.pass_context
def make(ctx):
    """Makes new migrations for all or the specified schema"""

    make_migrations(ctx.obj['schema'])


@click.group(cls=DYMGroup)
@click.pass_context
def config(ctx):
    """Configuration management operations (GROUP)"""

    from hfos.schemata.component import ComponentConfigSchemaTemplate
    ctx.obj['col'] = model_factory(ComponentConfigSchemaTemplate)


cli.add_command(config)


@config.command(short_help="Delete component configuration")
@click.argument('componentname')
@click.pass_context
def delete(ctx, componentname):
    """Delete an existing component configuration. This will trigger
    the creation of its default configuration upon next restart."""
    col = ctx.obj['col']

    if col.count({'name': componentname}) > 1:
        log('More than one component configuration of this name! Try '
            'one of the uuids as argument. Get a list with "config '
            'list"')
        return

    log('Deleting component configuration', componentname,
        emitter='MANAGE')
    config = col.find_one({'name': componentname})
    if config is None:
        log('Component configuration not found:', componentname,
            emitter='MANAGE')
        return
    config.delete()
    log('Done')


@config.command(short_help="Show component configurations")
@click.option('--component', default=None)
@click.pass_context
def show(ctx, component):
    """Show the stored, active configuration of a component."""

    col = ctx.obj['col']

    if col.count({'name': component}) > 1:
        log('More than one component configuration of this name! Try '
            'one of the uuids as argument. Get a list with "config '
            'list"')
        return

    if component is None:
        configurations = col.find()
        for configuration in configurations:
            log("%-10s : %s" % (configuration.name,
                                configuration.uuid),
                emitter='MANAGE')
    else:
        configuration = col.find_one({'name': component})

        print(json.dumps(configuration.serializablefields(), indent=4))


@db.group(cls=DYMGroup)
@click.option("--username", help="Username for user related operations",
              default=None)
@click.option("--password", help="Password for user related operations - supplying this via argument is unsafe",
              default=None)
@click.pass_context
def user(ctx, username, password):
    """User management operations (GROUP)"""

    ctx.obj['username'] = username
    ctx.obj['password'] = password


db.add_command(user)


def _create_user(ctx):
    username, passhash = _get_credentials(ctx.obj['username'],
                                          ctx.obj['password'],
                                          ctx.obj['db'])

    if ctx.obj['db'].objectmodels['user'].count({'name': username}) > 0:
        raise KeyError()

    new_user = ctx.obj['db'].objectmodels['user']({'uuid': str(uuid4())})

    new_user.name = username
    new_user.passhash = passhash

    return new_user


@user.command(short_help='create new user')
@click.pass_context
def create_user(ctx):
    """Creates a new local user"""

    try:
        new_user = _create_user(ctx)

        new_user.save()
        log("Done")
    except KeyError:
        log('User already exists', lvl=warn)


@user.command(short_help='create new admin')
@click.pass_context
def create_admin(ctx):
    """Creates a new local user and assigns admin role"""

    try:
        admin = _create_user(ctx)
        admin.roles.append('admin')

        admin.save()
        log("Done")
    except KeyError:
        log('User already exists', lvl=warn)


@user.command(short_help='delete user')
@click.option("--yes", "-y", help="Do not ask for confirmation",
              default=False, is_flag=True)
@click.pass_context
def delete_user(ctx, yes):
    """Delete a local user"""

    if ctx.obj['username'] is None:
        username = _ask("Please enter username:")
    else:
        username = ctx.obj['username']

    del_user = ctx.obj['db'].objectmodels['user'].find_one({'name': username})
    if yes or _ask('Confirm deletion', default=False, data_type='bool'):
        try:
            del_user.delete()
            log("Done")
        except AttributeError:
            log('User not found', lvl=warn)
    else:
        log("Cancelled")


@user.command(short_help="change user's password")
@click.pass_context
def change_password(ctx):
    """Change password of an existing user"""

    username, passhash = _get_credentials(ctx.obj['username'],
                                          ctx.obj['password'],
                                          ctx.obj['db'])

    change_user = ctx.obj['db'].objectmodels['user'].find_one({
        'name': username
    })
    if change_user is None:
        log('No such user', lvl=warn)
        return

    change_user.passhash = passhash
    change_user.save()

    log("Done")


@user.command(short_help='list local users')
@click.option('--search', help='Specify a term for searching', default=None,
              metavar='<text>')
@click.option('--uuid', help='Print user''s uuid as well',
              default=False, is_flag=True)
@click.pass_context
def list_users(ctx, search, uuid):
    """List all locally known users"""

    users = ctx.obj['db'].objectmodels['user']

    for found_user in users.find():
        if not search or (search and search in found_user.name):
            # TODO: Not 2.x compatible
            print(found_user.name, end=' ' if uuid else '\n')
            if uuid:
                print(found_user.uuid)

    log("Done")


@user.command(short_help='add role to user')
@click.option('--role', help='Specifies the new role', metavar='<name>')
@click.pass_context
def add_role(ctx, role):
    """Grant a role to an existing user"""

    if role is None:
        log('Specify the role with --role')
        return
    if ctx.obj['username'] is None:
        log('Specify the username with --username')
        return

    change_user = ctx.obj['db'].objectmodels['user'].find_one({
        'name': ctx.obj['username']
    })
    if role not in change_user.roles:
        change_user.roles.append(role)
        change_user.save()
        log('Done')
    else:
        log('User already has that role!', lvl=warn)


@click.group(cls=DYMGroup)
@click.option('--port', help='Specify local HFOS port', default=8055)
@click.pass_context
def install(ctx, port):
    """Install various aspects of HFOS (GROUP)"""

    ctx.obj['port'] = port


@install.command(short_help='build and install docs')
@click.option('--clear', help='Clears target documentation '
                              'folders', default=False, is_flag=True)
@click.pass_context
def docs(ctx, clear):
    """Build and install documentation"""

    install_docs(str(ctx.obj['instance']), clear)


def install_docs(instance, clear):
    """Builds and installs the complete HFOS documentation."""

    _check_root()

    def make_docs():
        """Trigger a Sphinx make command to build the documentation."""
        log("Generating HTML documentation")

        try:
            build = Popen(
                [
                    'make',
                    'html'
                ],
                cwd='docs/'
            )

            build.wait()
        except Exception as e:
            log("Problem during documentation building: ", e, type(e),
                exc=True, lvl=error)
            return False
        return True

    make_docs()

    # If these need changes, make sure they are watertight and don't remove
    # wanted stuff!
    target = os.path.join('/var/lib/hfos', instance, 'frontend/docs')
    source = 'docs/build/html'

    log("Updating documentation directory:", target)

    if not os.path.exists(os.path.join(os.path.curdir, source)):
        log(
            "Documentation not existing yet. Run python setup.py "
            "build_sphinx first.", lvl=error)
        return

    if os.path.exists(target):
        log("Path already exists: " + target)
        if clear:
            log("Cleaning up " + target, lvl=warn)
            shutil.rmtree(target)

    log("Copying docs to " + target)
    copy_tree(source, target)
    log("Done: Install Docs")


@install.command(short_help='create structures in /var')
@click.option('--clear', help='Clears already existing cache '
                              'directories', is_flag=True, default=False)
@click.option('--clear-all', help='Clears all already existing '
                                  'directories', is_flag=True, default=False)
@click.pass_context
def var(ctx, clear, clear_all):
    """Install variable data to /var/[lib,cache]/hfos"""

    install_var(str(ctx.obj['instance']), clear, clear_all)


def install_var(instance, clear, clear_all):
    """Install required folders in /var"""
    _check_root()

    log("Checking frontend library and cache directories",
        emitter='MANAGE')

    uid = pwd.getpwnam("hfos").pw_uid
    gid = grp.getgrnam("hfos").gr_gid

    join = os.path.join

    # If these need changes, make sure they are watertight and don't remove
    # wanted stuff!
    target_paths = (
        '/var/www/challenges',  # For LetsEncrypt acme certificate challenges
        join('/var/lib/hfos', instance),
        join('/var/local/hfos', instance),
        join('/var/local/hfos', instance, 'backup'),
        join('/var/cache/hfos', instance),
        join('/var/cache/hfos', instance, 'tilecache'),
        join('/var/cache/hfos', instance, 'rastertiles'),
        join('/var/cache/hfos', instance, 'rastercache')
    )
    logfile = "/var/log/hfos-" + instance + ".log"

    for item in target_paths:
        if os.path.exists(item):
            log("Path already exists: " + item)
            if clear_all or (clear and 'cache' in item):
                log("Cleaning up: " + item, lvl=warn)
                shutil.rmtree(item)

        if not os.path.exists(item):
            log("Creating path: " + item)
            os.mkdir(item)
            os.chown(item, uid, gid)

    # Touch logfile to make sure it exists
    open(logfile, "a").close()
    os.chown(logfile, uid, gid)

    log("Done: Install Var")


@install.command(short_help='install provisions')
@click.option('--provision', '-p', help="Specify a provision (default=install "
                                        "all)",
              default=None, metavar='<name>')
@click.option('--clear', help='Clears already existing collections (DANGER!)',
              is_flag=True, default=False)
@click.option('--overwrite', '-o', help='Overwrites existing provisions',
              is_flag=True, default=False)
@click.option('--list-provisions', '-l', help='Only list available provisions',
              is_flag=True, default=False)
@click.option('--dbhost', default=db_host_default, help=db_host_help)
@click.option('--dbname', default=db_default, help=db_help,
              metavar=db_metavar)
def provisions(provision, dbhost, dbname, clear, overwrite, list_provisions):
    """Install default provisioning data"""

    install_provisions(provision, dbhost, dbname, clear, overwrite, list_provisions)


def install_provisions(provision, dbhost, dbname='hfos', clear=False, overwrite=False, list_provisions=False):
    """Install default provisioning data"""

    log("Installing HFOS default provisions")

    # from hfos.logger import verbosity, events
    # verbosity['console'] = verbosity['global'] = events
    from hfos import database
    database.initialize(dbhost, dbname)

    from hfos.provisions import provisionstore

    if list_provisions:
        exit()

    if provision is not None:
        if provision in provisionstore:
            log("Provisioning ", provision)
            provisionstore[provision](overwrite=overwrite, clear=clear)
        else:
            log("Unknown provision: ", provision, "\nValid provisions are",
                list(provisionstore.keys()),
                lvl=error,
                emitter='MANAGE')
    else:
        for provision_name in provisionstore:
            log("Provisioning " + provision_name)
            provisionstore[provision_name](overwrite=overwrite, clear=clear)

    log("Done: Install Provisions")


@install.command(short_help='install modules')
@click.option('--wip', help="Install Work-In-Progress (alpha/beta-state) modules as well", is_flag=True)
def modules(wip):
    """Install the plugin modules"""

    install_modules(wip)


def install_modules(wip):
    """Install the plugin modules"""

    def install_module(hfos_module):
        """Install a single module via setuptools"""
        try:
            setup = Popen(
                [
                    sys.executable,
                    'setup.py',
                    'develop'
                ],
                cwd='modules/' + hfos_module + "/"
            )

            setup.wait()
        except Exception as e:
            log("Problem during module installation: ", hfos_module, e,
                type(e), exc=True, lvl=error)
            return False
        return True

    modules_production = [
        # TODO: Poor man's dependency management, as long as the modules are
        # installed from local sources and they're not available on pypi,
        # which would handle real dependency management for us:
        'navdata',

        # Now all the rest:
        'alert',
        'automat',
        'busrepeater',
        'camera',
        'chat',
        'calendar',
        'countables',
        'crew',
        'dash',
        # 'dev',
        'enrol',
        'maps',
        'nmea',
        'nodestate',
        'polls',
        'project',
        'shareables',
        'webguides',
        'wiki'
    ]

    modules_wip = [
        'calc',
        'comms',
        'contacts',
        'equipment',
        'filemanager',
        'garden',
        'heroic',
        'ldap',
        'library',
        'logbook',
        'mesh',
        'protocols',
        'robot',
        'switchboard',
    ]

    installables = modules_production

    if wip:
        installables.extend(modules_wip)

    success = []
    failed = []

    for installable in installables:
        log('Installing module ', installable)
        if install_module(installable):
            success.append(installable)
        else:
            failed.append(installable)

    log('Installed modules: ', success)
    if len(failed) > 0:
        log('Failed modules: ', failed)
    log('Done: Install Modules')


@install.command(short_help='install systemd service')
@click.pass_context
def service(ctx):
    """Install systemd service configuration"""

    install_service(ctx.obj['instance'], ctx.obj['dbhost'], ctx.obj['dbname'], ctx.obj['port'])


def install_service(instance, dbhost, dbname, port):
    """Install systemd service configuration"""

    _check_root()

    log("Installing systemd service")

    launcher = os.path.realpath(__file__).replace('manage', 'launcher')
    executable = sys.executable + " " + launcher
    executable += " --instance " + instance
    executable += " --dbname " + dbname + " --dbhost " + dbhost
    executable += " --port " + port
    executable += " --dolog --logfile /var/log/hfos-" + instance + ".log"
    executable += " --logfileverbosity 30 -q"

    definitions = {
        'instance': instance,
        'executable': executable
    }
    service_name = 'hfos.' + instance + '.service'

    write_template_file(os.path.join('dev/templates', service_template),
                        os.path.join('/etc/systemd/system/', service_name),
                        definitions)

    Popen([
        'systemctl',
        'enable',
        service_name
    ])

    log('Launching service')

    Popen([
        'systemctl',
        'start',
        service_name
    ])

    log("Done: Install Service")


@install.command(short_help='install nginx configuration')
@click.option('--hostname', default=None,
              help='Override public Hostname (FQDN) Default from active system '
                   'configuration')
@click.pass_context
def nginx(ctx, hostname):
    """Install nginx configuration"""

    install_nginx(ctx.obj['dbhost'], ctx.obj['dbname'], ctx.obj['port'], hostname)


def install_nginx(instance, dbhost, dbname, port, hostname=None):
    """Install nginx configuration"""

    _check_root()

    log("Installing nginx configuration")

    if hostname is None:
        try:
            config = _get_system_configuration(dbhost, dbname)
            hostname = config.hostname
        except Exception as e:
            log('Exception:', e, type(e), exc=True, lvl=error)
            log("""Could not determine public fully qualified hostname!
Check systemconfig (see db view and db modify commands) or specify
manually with --hostname host.domain.tld

Using 'localhost' for now""", lvl=warn)
            hostname = 'localhost'

    definitions = {
        'instance': instance,
        'server_public_name': hostname,
        'ssl_certificate': cert_file,
        'ssl_key': key_file,
        'host_url': 'http://127.0.0.1:%i/' % port
    }

    if distribution == 'DEBIAN':
        configuration_file = '/etc/nginx/sites-available/hfos.%s.conf' % instance
        configuration_link = '/etc/nginx/sites-enabled/hfos.%s.conf' % instance
    elif distribution == 'ARCH':
        configuration_file = '/etc/nginx/nginx.conf'
        configuration_link = None
    else:
        log('Unsure how to proceed, you may need to specify your '
            'distribution', lvl=error)
        return

    log('Writing nginx HFOS site definition')
    write_template_file(os.path.join('dev/templates', nginx_configuration),
                        configuration_file,
                        definitions)

    if configuration_link is not None:
        log('Enabling nginx HFOS site (symlink)')
        if not os.path.exists(configuration_link):
            os.symlink(configuration_file, configuration_link)

    log('Restarting nginx service')
    Popen([
        'systemctl',
        'restart',
        'nginx.service'
    ])

    log("Done: Install nginx configuration")


@install.command(short_help='create system user')
def system_user():
    """Install HFOS system user (hfos.hfos)"""

    install_system_user()
    log("Done: Setup User")


def install_system_user():
    """Install HFOS system user (hfos.hfos)"""

    _check_root()

    Popen([
        '/usr/sbin/adduser',
        '--system',
        '--quiet',
        '--home',
        '/var/run/hfos',
        '--group',
        '--disabled-password',
        '--disabled-login',
        'hfos'
    ])
    time.sleep(2)


@install.command(short_help='install ssl certificate')
@click.option('--selfsigned', help="Use a self-signed certificate",
              default=True, is_flag=True)
def cert(selfsigned):
    """Install a local SSL certificate"""

    install_cert(selfsigned)


def install_cert(selfsigned):
    """Install a local SSL certificate"""

    _check_root()

    if selfsigned:
        log('Generating self signed (insecure) certificate/key '
            'combination')

        try:
            os.mkdir('/etc/ssl/certs/hfos')
        except FileExistsError:
            pass
        except PermissionError:
            log("Need root (e.g. via sudo) to generate ssl certificate")
            sys.exit(1)

        def create_self_signed_cert():
            """Create a simple self signed SSL certificate"""

            # create a key pair
            k = crypto.PKey()
            k.generate_key(crypto.TYPE_RSA, 1024)

            if os.path.exists(cert_file):
                try:
                    certificate = open(cert_file, "r").read()
                    old_cert = crypto.load_certificate(crypto.FILETYPE_PEM,
                                                       certificate)
                    serial = old_cert.get_serial_number() + 1
                except (crypto.Error, OSError) as e:
                    log('Could not read old certificate to increment '
                        'serial:', type(e), e, exc=True, lvl=warn)
                    serial = 1
            else:
                serial = 1

            # create a self-signed certificate
            certificate = crypto.X509()
            certificate.get_subject().C = "DE"
            certificate.get_subject().ST = "Berlin"
            certificate.get_subject().L = "Berlin"
            certificate.get_subject().O = "Hackerfleet"
            certificate.get_subject().OU = "Hackerfleet"
            certificate.get_subject().CN = gethostname()
            certificate.set_serial_number(serial)
            certificate.gmtime_adj_notBefore(0)
            certificate.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
            certificate.set_issuer(certificate.get_subject())
            certificate.set_pubkey(k)
            certificate.sign(k, 'sha512')

            open(key_file, "wt").write(str(
                crypto.dump_privatekey(crypto.FILETYPE_PEM, k),
                encoding="ASCII"))

            open(cert_file, "wt").write(str(
                crypto.dump_certificate(crypto.FILETYPE_PEM, certificate),
                encoding="ASCII"))

            open(combined_file, "wt").write(str(
                crypto.dump_certificate(crypto.FILETYPE_PEM, certificate),
                encoding="ASCII") + str(
                crypto.dump_privatekey(crypto.FILETYPE_PEM, k),
                encoding="ASCII"))

        create_self_signed_cert()

        log('Done: Install Cert')
    else:

        # TODO

        log('Not implemented yet. You can build your own certificate and '
            'store it in /etc/ssl/certs/hfos/server-cert.pem - it should '
            'be a certificate with key, as this is used server side and '
            'there is no way to enter a separate key.', lvl=error)


@install.command(short_help='build and install frontend')
@click.option('--dev', help="Use frontend development (./frontend) location",
              default=False, is_flag=True)
@click.option('--rebuild', help="Rebuild frontend before installation",
              default=False, is_flag=True)
@click.option('--build-type', help="Specify frontend build type. Either dist(default) or build",
              default='dist')
@click.pass_context
def frontend(ctx, dev, rebuild, build_type):
    """Build and install frontend"""

    install_frontend(instance=ctx.obj['instance'], forcerebuild=rebuild, development=dev, build_type=build_type)


@install.command('all', short_help='install everything')
@click.option('--clear', help='Clears already existing cache '
                              'directories and data', is_flag=True,
              default=False)
@click.pass_context
def install_all(ctx, clear):
    """Default-Install everything installable

    \b
    This includes
    * System user (hfos.hfos)
    * Self signed certificate
    * Variable data locations (/var/lib/hfos and /var/cache/hfos)
    * All the official modules in this repository
    * Default module provisioning data
    * Documentation
    * systemd service descriptor

    It does NOT build and install the HTML5 frontend."""

    _check_root()

    instance = ctx.obj['instance']
    dbhost = ctx.obj['dbhost']
    dbname = ctx.obj['dbname']
    port = ctx.obj['port']

    install_system_user()
    install_cert(selfsigned=True)

    install_var(instance, clear=clear, clear_all=clear)
    install_modules(wip=False)
    install_provisions(provision='user', dbhost=db_host_default, clear=clear)
    install_provisions(provision=None, dbhost=db_host_default, clear=clear)
    install_docs(instance, clear=clear)

    install_service(instance, dbhost, dbname, port)
    install_nginx(instance, dbhost, dbname, port)

    log('Done')


cli.add_command(install)


@click.command(short_help='remove stuff in /var')
def uninstall():
    """Uninstall data and resource locations"""

    _check_root()

    response = _ask("This will delete all data of your HFOS installations! Type"
                    "YES to continue:", default="N", show_hint=False)
    if response == 'YES':
        shutil.rmtree('/var/lib/hfos')
        shutil.rmtree('/var/cache/hfos')


cli.add_command(uninstall)


@db.command(short_help='modify field values of objects')
@click.option("--schema")
@click.option("--uuid")
@click.option("--filter")
@click.argument('field')
@click.argument('value')
@click.pass_context
def modify(ctx, schema, uuid, filter, field, value):
    """Modify field values of objects"""
    database = ctx.obj['db']

    model = database.objectmodels[schema]
    obj = None

    if uuid:
        obj = model.find_one({'uuid': uuid})
    elif filter:
        obj = model.find_one(literal_eval(filter))
    else:
        log('No object uuid or filter specified.',
            lvl=error)

    if obj is None:
        log('No object found',
            lvl=error)
        return

    log('Object found, modifying', lvl=debug)
    try:
        new_value = literal_eval(value)
    except ValueError:
        log('Interpreting value as string')
        new_value = str(value)

    obj._fields[field] = new_value
    obj.validate()
    log('Changed object validated', lvl=debug)
    obj.save()
    log('Done')


@db.command(short_help='view objects')
@click.option("--schema", default=None)
@click.option("--uuid", default=None)
@click.option("--filter", default=None)
@click.pass_context
def view(ctx, schema, uuid, filter):
    """Show stored objects"""

    database = ctx.obj['db']

    if schema is None:
        log('No schema given. Read the help', lvl=warn)
        return

    model = database.objectmodels[schema]

    if uuid:
        obj = model.find({'uuid': uuid})
    elif filter:
        obj = model.find(literal_eval(filter))
    else:
        obj = model.find()

    for item in obj:
        pprint(item._fields)


@db.command(short_help='Validates stored objects')
@click.option("--schema", "-s", default=None, help="Specify object schema to validate")
@click.option("--all", help="Agree to validate all objects, if no schema given", is_flag=True)
@click.pass_context
def validate(ctx, schema, all):
    """Validates all objects or all objects of a given schema."""

    database = ctx.obj['db']

    if schema is None:
        if all is False:
            log('No schema given. Read the help', lvl=warn)
            return
        else:
            schemata = database.objectmodels.keys()
    else:
        schemata = [schema]

    for schema in schemata:
        try:
            for obj in database.objectmodels[schema].find():
                obj.validate()
        except Exception as e:

            log('Exception while validating:',
                schema, e, type(e),
                '\n\nFix this object and rerun validation!',
                emitter='MANAGE', lvl=error)

    log('Done')


@db.command(short_help='export objects to json')
@click.option("--schema", "-s", default=None, help="Specify schema to export")
@click.option("--uuid", "-u", default=None, help="Specify single object to export")
@click.option("--filter", default=None, help="Find objects to export by filter")
@click.option("--format", default='json', help="Currently only JSON is supported")
@click.option("--filename", "-f", default=None, help="Export to given file; Overwrites!")
@click.option("--pretty", "-p", default=False, is_flag=True, help="Indent output for human readability")
@click.option("--all", default=False, is_flag=True, help="Agree to export all documents, if no schema specified")
@click.option("--omit", "-o", multiple=True, default=[], help="Omit given fields (multiple, e.g. '-o _id -o perms')")
@click.pass_context
def export(ctx, schema, uuid, filter, format, filename, pretty, all, omit):
    """Export stored objects

    Warning! This functionality is work in progress and you may destroy live data by using it!
    Be very careful when using the export/import functionality!"""

    backup(schema, uuid, filter, format, filename, pretty, all, omit)


@db.command('import', short_help='import objects from json')
@click.option("--schema", default=None, help="Specify schema to import")
@click.option("--uuid", default=None, help="Specify single object to import")
@click.option("--filter", default=None, help="Specify objects to import by filter (Not implemented yet!)")
@click.option("--format", default='json', help="Currently only JSON is supported")
@click.option("--filename", default=None, help="Import from given file")
@click.option("--all", default=False, is_flag=True, help="Agree to import all documents, if no schema specified")
@click.option("--dry", default=False, is_flag=True, help="Do not write changes to the database")
@click.pass_context
def cli_import(ctx, schema, uuid, filter, format, filename, all, dry):
    """Import objects from file

    Warning! This functionality is work in progress and you may destroy live data by using it!
    Be very careful when using the export/import functionality!"""

    format = format.upper()

    with open(filename, 'r') as f:
        json_data = f.read()
    data = json.loads(json_data)  # , parse_float=True, parse_int=True)

    if schema is None:
        if all is False:
            log('No schema given. Read the help', lvl=warn)
            return
        else:
            schemata = data.keys()
    else:
        schemata = [schema]

    database = ctx.obj['db']

    all_items = {}
    total = 0

    for schema_item in schemata:
        model = database.objectmodels[schema_item]

        objects = data[schema_item]
        if uuid:
            for item in objects:
                if item['uuid'] == uuid:
                    items = [model(item)]
        else:
            items = []
            for item in objects:
                thing = model(item)
                items.append(thing)

        schema_total = len(items)
        total += schema_total

        if dry:
            log('Would import', schema_total, 'items of', schema_item)
        all_items[schema_item] = items

    if dry:
        log('Would import', total, 'objects.')
    else:
        log('Importing', total, 'objects.')
        for schema_name, item_list in all_items.items():
            log('Importing', len(item_list), 'objects of type', schema_name)
            for item in item_list:
                item._fields['_id'] = bson.objectid.ObjectId(item._fields['_id'])
                item.save()


@db.command(short_help='find in object model fields')
@click.option("--search", help="Argument to search for in object model "
                               "fields",
              default=None, metavar='<text>')
@click.option("--by-type", help="Find all fields by type",
              default=False, is_flag=True)
@click.option('--obj', default=None, help="Search in specified object "
                                          "model", metavar='<name>')
@click.pass_context
def find_field(ctx, search, by_type, obj):
    """Find fields in registered data models."""

    # TODO: Fix this to work recursively on all possible subschemes
    if search is not None:
        search = search
    else:
        search = _ask("Enter search term")

    database = ctx.obj['db']

    def find(schema, search, by_type, result=[], key=""):
        """Examine a schema to find fields by type or name"""

        fields = schema['properties']
        if not by_type:
            if search in fields:
                result.append(key)
                # log("Found queried fieldname in ", model)
        else:
            for field in fields:
                try:
                    if "type" in fields[field]:
                        # log(fields[field], field)
                        if fields[field]["type"] == search:
                            result.append((key, field))
                            # log("Found field", field, "in", model)
                except KeyError as e:
                    log("Field access error:", e, type(e), exc=True,
                        lvl=debug)

        if 'properties' in fields:
            # log('Sub properties checking:', fields['properties'])
            result.append(find(fields['properties'], search, by_type,
                               result, key=fields['name']))

        for field in fields:
            if 'items' in fields[field]:
                if 'properties' in fields[field]['items']:
                    # log('Sub items checking:', fields[field])
                    result.append(find(fields[field]['items'], search,
                                       by_type, result, key=field))
                else:
                    pass
                    # log('Items without proper definition!')

        return result

    if obj is not None:
        schema = database.objectmodels[obj]._schema
        result = find(schema, search, by_type, [], key="top")
        if result:
            # log(args.object, result)
            print(obj)
            pprint(result)
    else:
        for model, thing in database.objectmodels.items():
            schema = thing._schema

            result = find(schema, search, by_type, [], key="top")
            if result:
                print(model)
                # log(model, result)
                print(result)


@db.command(short_help='Find illegal _id fields')
@click.option('--delete', default=False, is_flag=True, help='Delete found duplicates')
@click.option('--fix', default=False, is_flag=True, help='Tries to fix faulty object ids')
@click.option('--test', default=False, is_flag=True, help='Test if faulty objects have clones with correct ids')
@click.option('--schema', default=None, help='Work on specified schema only')
@click.pass_context
def illegalcheck(ctx, schema, delete, fix, test):
    database = ctx.obj['db']
    verbose = ctx.obj['verbose']

    if delete and fix:
        log('Delete and fix operations are exclusive.')
        return

    if schema is None:
        schemata = database.objectmodels.keys()
    else:
        schemata = [schema]

    for thing in schemata:
        log('Schema:', thing)
        for item in database.objectmodels[thing].find():
            if not isinstance(item._fields['_id'], bson.objectid.ObjectId):
                if not delete or verbose:
                    log(item.uuid)
                    if verbose:
                        log(item._fields, pretty=True)
                if test:
                    if database.objectmodels[thing].count({'uuid': item.uuid}) == 1:
                        log('Only a faulty object exists.')
                if delete:
                    item.delete()
                if fix:
                    _id = item._fields['_id']
                    item._fields['_id'] = bson.objectid.ObjectId(_id)
                    assert isinstance(item._fields['_id'], bson.objectid.ObjectId)
                    item.save()
                    database.objectmodels[thing].find_one({'_id': _id}).delete()


@db.command(short_help='Find duplicates by UUID')
@click.option('--delete', default=False, is_flag=True, help='Delete found duplicates')
@click.option('--merge', default=False, is_flag=True, help='Merge found duplicates')
@click.option('--schema', default=None, help='Work on specified schema only')
@click.pass_context
def dupcheck(ctx, delete, merge, schema):
    database = ctx.obj['db']
    verbose = ctx.obj['verbose']

    if schema is None:
        schemata = database.objectmodels.keys()
    else:
        schemata = [schema]

    for thing in schemata:
        dupes = {}
        dupe_count = 0
        count = 0

        for item in database.objectmodels[thing].find():
            if item.uuid in dupes:
                dupes[item.uuid].append(item)
                dupe_count += 1
            else:
                dupes[item.uuid] = [item]
            count += 1

        if len(dupes) > 0:
            log(dupe_count, 'duplicates of', count, 'items total of type', thing, 'found:')
            if verbose:
                log(dupes.keys(), pretty=True)

        if delete:
            log('Deleting duplicates')
            for item in dupes:
                database.objectmodels[thing].find_one({'uuid': item}).delete()

            log('Done for schema', thing)
        elif merge:

            def merge(a, b, path=None):
                "merges b into a"
                if path is None: path = []
                for key in b:
                    if key in a:
                        if isinstance(a[key], dict) and isinstance(b[key], dict):
                            merge(a[key], b[key], path + [str(key)])
                        elif a[key] == b[key]:
                            pass  # same leaf value
                        else:
                            log('Conflict at', path, key, ':', a[key], '<->', b[key])
                            resolve = ''
                            while resolve not in ('a', 'b'):
                                resolve = _ask('Choose? (a or b)')
                            if resolve == 'a':
                                b[key] = a[key]
                            else:
                                a[key] = b[key]
                    else:
                        a[key] = b[key]
                return a

            if verbose:
                log(dupes, pretty=True)
            for item in dupes:
                if len(dupes[item]) == 1:
                    continue
                ignore = False
                while len(dupes[item]) > 1 or ignore is False:
                    log(len(dupes[item]), 'duplicates found:')
                    for index, dupe in enumerate(dupes[item]):
                        log('Candidate #', index, ':')
                        log(dupe._fields, pretty=True)
                    request = _ask('(d)iff, (m)erge, (r)emove, (i)gnore, (q)uit?')
                    if request == 'q':
                        log('Done')
                        return
                    elif request == 'i':
                        ignore = True
                        break
                    elif request == 'r':
                        delete_request = -2
                        while delete_request == -2 or -1 > delete_request > len(dupes[item]):
                            delete_request = _ask('Which one? (0-%i or -1 to cancel)' % (len(dupes[item]) - 1),
                                                  data_type='int')
                        if delete_request == -1:
                            continue
                        else:
                            log('Deleting candidate #', delete_request)
                            dupes[item][delete_request].delete()
                            break
                    elif request in ('d', 'm'):
                        merge_request_a = -2
                        merge_request_b = -2

                        while merge_request_a == -2 or -1 > merge_request_a > len(dupes[item]):
                            merge_request_a = _ask('Merge from? (0-%i or -1 to cancel)' % (len(dupes[item]) - 1),
                                                   data_type='int')
                        if merge_request_a == -1:
                            continue

                        while merge_request_b == -2 or -1 > merge_request_b > len(dupes[item]):
                            merge_request_b = _ask('Merge into? (0-%i or -1 to cancel)' % (len(dupes[item]) - 1),
                                                   data_type='int')
                        if merge_request_b == -1:
                            continue

                        log(deepdiff.DeepDiff(dupes[item][merge_request_a]._fields,
                                              dupes[item][merge_request_b]._fields), pretty=True)

                        if request == 'm':
                            log('Merging candidates', merge_request_a, 'and', merge_request_b)

                            _id = dupes[item][merge_request_b]._fields['_id']
                            if not isinstance(_id, bson.objectid.ObjectId):
                                _id = bson.objectid.ObjectId(_id)

                            dupes[item][merge_request_a]._fields['_id'] = _id
                            merge(dupes[item][merge_request_b]._fields, dupes[item][merge_request_a]._fields)
                            log('Candidate after merge:', dupes[item][merge_request_b]._fields, pretty=True)
                            store = ''
                            while store not in ('n', 'y'):
                                store = _ask('Store?')
                            if store == 'y':
                                dupes[item][merge_request_b].save()
                                dupes[item][merge_request_a].delete()
                                break

        log('Done')


@cli.command(short_help='Start interactive management shell')
def shell():
    """Open an shell to work with the manage tool interactively."""

    prompt_kwargs = {
        'history': FileHistory('/tmp/.hfos-manage.history'),
    }
    print("""HFOS - Management Tool Interactive Prompt

Type -h for help, tab completion is available, hit Ctrl-D to quit.""")
    repl(click.get_current_context(), prompt_kwargs=prompt_kwargs)


if __name__ == '__main__':
    cli(obj={})

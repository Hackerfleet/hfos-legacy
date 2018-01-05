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

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""

HFOS Management Tool
====================

This is the management tool utility to install, configure and maintain
Hackerfleet Operating System installations.

"""

import click
import csv
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

# 2.x/3.x imports: (TODO: Simplify those, one 2x/3x ought to be enough)
try:
    # noinspection PyUnresolvedReferences
    input = raw_input  # NOQA
except NameError:
    pass

try:
    from subprocess import Popen, PIPE
except ImportError:
    # noinspection PyUnresolvedReferences,PyUnresolvedReferences,
    # PyUnresolvedReferences
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


def _check_root():
    """Check if current user has root permissions"""

    if os.geteuid() != 0:
        hfoslog("Need root access to install. Use sudo!", lvl=error)
        hfoslog("If you installed into a virtual environment, don't forget to "
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
        hfoslog("Making directory '%s'" % real_path, emitter='MANAGE')
        os.makedirs(real_path)

    # pprint(info)
    for item in templates.values():
        source = os.path.join('dev/templates', item[0])
        filename = os.path.abspath(
            os.path.join(target, item[1].format(**info)))
        hfoslog("Creating file from template '%s'" % filename,
                emitter='MANAGE')
        write_template_file(source, filename, info)


def _ask(question, default=None, data_type=str, show_hint=False):
    """Interactively ask the user for data"""

    data = default

    if data_type == bool:
        data = None
        while data not in ('Y', 'J', 'N', '1', '0'):
            data = input(
                "%s? [%s]: " % (question, default.upper())).upper()

            if default and data == '':
                return default

        return data in ('Y', 'J', '1')

    elif data_type in (str, unicode):
        if show_hint:
            msg = "%s? [%s] (%s): " % (question, default, data_type)
        else:
            msg = question

        data = input(msg)

        if len(data) == 0:
            data = default

    return data


def _ask_questionnaire():
    """Asks questions to fill out a HFOS plugin template"""

    answers = {}
    print(info_header)
    pprint(questions.items())

    for question, default in questions.items():
        response = _ask(question, default, type(default), show_hint=True)
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
        hfoslog('No systemconfig or it is without a salt! '
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


def _get_system_configuration():
    from hfos import database
    database.initialize()
    systemconfig = database.objectmodels['systemconfig'].find_one({
        'active': True
    })

    return systemconfig


@with_plugins(iter_entry_points('hfos.management'))
@click.group(context_settings={'help_option_names': ['-h', '--help']},
             cls=DYMGroup)
@click.option('--quiet', default=False, help="Suppress all output",
              is_flag=True)
@click.option('--log', default=20, help='Log level to use (0-100)',
              metavar='<number>')
@click.pass_context
def cli(ctx, quiet, log):
    """HFOS Management Utility

    This utility supports various operations to manage HFOS installations.
    Most of the commands are grouped. To obtain more information about the
    groups' available sub commands, try

    hfos_manage group --help

    To display details of a command, try

    hfos_manage group command --help
    """

    ctx.obj['quiet'] = quiet
    verbosity['console'] = log
    verbosity['global'] = log


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
            hfoslog("Target exists! Use --clear to delete it first.",
                    emitter='MANAGE')
            sys.exit(2)

    done = False
    info = None

    while not done:
        info = _ask_questionnaire()
        pprint(info)
        done = _ask('Is the above correct', default='y', data_type=bool)

    augmented_info = _augment_info(info)

    hfoslog("Constructing module %(plugin_name)s" % info, emitter='MANAGE')
    _construct_module(augmented_info, target)


db_host_default = '127.0.0.1:27017'
db_host_help = 'Define hostname for database server (default: ' + \
               db_host_default + ')'
db_host_metavar = '<ip:port>'


@click.group(cls=DYMGroup)
@click.option('--dbhost', default=db_host_default, help=db_host_help,
              metavar=db_host_metavar)
@click.pass_context
def db(ctx, dbhost):
    """Database management operations (GROUP)"""

    from hfos import database
    database.initialize(dbhost)
    ctx.obj['db'] = database


cli.add_command(db)


@db.command(short_help='Irrevocably remove collection content')
@click.argument('schema')
def clear(schema):
    """Clears an entire database collection irrevocably. Use with caution!"""

    response = _ask('Are you sure you want to delete the collection "%s"' % (
        schema), default='N', data_type=bool)
    if response is True:
        # TODO: Fix this to make use of the dbhost

        client = pymongo.MongoClient(host="localhost", port=27017)
        db = client["hfos"]

        hfoslog("Clearing collection for", schema, lvl=warn,
                emitter='MANAGE')
        db.drop_collection(schema)


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
@click.option('--dbhost', default=db_host_default, help=db_host_help,
              metavar=db_host_metavar)
@click.pass_context
def config(ctx, dbhost):
    """Configuration management operations (GROUP)"""

    from hfos import database
    database.initialize(dbhost)
    ctx.obj['db'] = database

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
        hfoslog('More than one component configuration of this name! Try '
                'one of the uuids as argument. Get a list with "config '
                'list"', emitter='MANAGE')
        return

    hfoslog('Deleting component configuration', componentname,
            emitter='MANAGE')
    config = col.find_one({'name': componentname})
    if config is None:
        hfoslog('Component configuration not found:', componentname,
                emitter='MANAGE')
        return
    config.delete()
    hfoslog('Done', emitter='MANAGE')


@config.command(short_help="Show component configurations")
@click.option('--component', default=None)
@click.pass_context
def show(ctx, component):
    """Show the stored, active configuration of a component."""

    col = ctx.obj['col']

    if col.count({'name': component}) > 1:
        hfoslog('More than one component configuration of this name! Try '
                'one of the uuids as argument. Get a list with "config '
                'list"', emitter='MANAGE')
        return

    if component is None:
        configurations = col.find()
        for configuration in configurations:
            hfoslog("%-10s : %s" % (configuration.name,
                                    configuration.uuid),
                    emitter='MANAGE')
    else:
        configuration = col.find_one({'name': component})

        print(json.dumps(configuration.serializablefields(), indent=4))


@db.group(cls=DYMGroup)
@click.option("--username", help="Username for user related operations",
              default=None)
@click.option("--password", help="Password for user related operations",
              default=None)
@click.pass_context
def user(ctx, username, password):
    """User management operations (GROUP)"""

    ctx.obj['username'] = username
    ctx.obj['password'] = password


db.add_command(user)


@user.command(short_help='create new user')
@click.pass_context
def create_user(ctx):
    """Creates a new local user"""

    username, passhash = _get_credentials(ctx.obj['username'],
                                          ctx.obj['password'],
                                          ctx.obj['db'])

    new_user = ctx.obj['db'].objectmodels['user']({'uuid': str(uuid4())})

    new_user.name = username
    new_user.passhash = passhash

    # pprint(user._fields)
    try:
        new_user.save()
        hfoslog("Done!", emitter='MANAGE')
    except DuplicateKeyError:
        hfoslog('User already exists', lvl=warn, emitter='MANAGE')


@user.command(short_help='delete user')
@click.pass_context
def delete_user(ctx):
    """Delete a local user"""

    if ctx.obj['username'] is None:
        username = _ask("Please enter username: ")
    else:
        username = ctx.obj['username']

    del_user = ctx.obj['db'].objectmodels['user'].find_one({'name': username})
    # TODO: Verify back if not --yes in args
    del_user.delete()

    hfoslog("Done!", emitter='MANAGE')


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
        hfoslog('No such user', lvl=warn, emitter='MANAGE')
        return

    change_user.passhash = passhash
    change_user.save()

    hfoslog("Done!", emitter='MANAGE')


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

    hfoslog("Done!", emitter='MANAGE')


@user.command(short_help='add role to user')
@click.option('--role', help='Specifies the new role', metavar='<name>')
@click.pass_context
def add_role(ctx, role):
    """Grant a role to an existing user"""

    if role is None:
        hfoslog('Specify the role with --role')
        return
    if ctx.obj['username'] is None:
        hfoslog('Specify the username with --username')
        return

    change_user = ctx.obj['db'].objectmodels['user'].find_one({
        'name': ctx.obj['username']
    })
    if role not in change_user.roles:
        change_user.roles.append(role)
        change_user.save()
        hfoslog('Done', emitter='MANAGE')
    else:
        hfoslog('User already has that role!', lvl=warn, emitter='MANAGE')


@click.group(cls=DYMGroup)
def install():
    """Install various aspects of HFOS (GROUP)"""
    pass


@install.command(short_help='build and install docs')
@click.option('--clear', help='Clears target documentation '
                              'folders', default=False, is_flag=True)
def docs(clear):
    """Build and install documentation"""

    install_docs(clear)


def install_docs(clear):
    """Builds and installs the complete HFOS documentation."""

    _check_root()

    def make_docs():
        """Trigger a Sphinx make command to build the documentation."""
        hfoslog("Generating HTML documentation", emitter='MANAGE')

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
            hfoslog("Problem during documentation building: ", e, type(e),
                    exc=True, emitter='MANAGE', lvl=error)
            return False
        return True

    make_docs()

    hfoslog("Updating documentation directory", emitter='MANAGE')

    # If these need changes, make sure they are watertight and don't remove
    # wanted stuff!
    target = '/var/lib/hfos/frontend/docs'
    source = 'docs/build/html'

    if not os.path.exists(os.path.join(os.path.curdir, source)):
        hfoslog(
            "Documentation not existing yet. Run python setup.py "
            "build_sphinx first.", emitter='MANAGE', lvl=error)
        return

    if os.path.exists(target):
        hfoslog("Path already exists: " + target, emitter='MANAGE')
        if clear:
            hfoslog("Cleaning up " + target, emitter='MANAGE', lvl=warn)
            shutil.rmtree(target)

    hfoslog("Copying docs to " + target, emitter='MANAGE')
    copy_tree(source, target)
    hfoslog("Done: Install Docs")


@install.command(short_help='create structures in /var')
@click.option('--clear', help='Clears already existing cache '
                              'directories', is_flag=True, default=False)
@click.option('--clear-all', help='Clears all already existing '
                                  'directories', is_flag=True, default=False)
def var(clear, clear_all):
    """Install variable data to /var/[lib,cache]/hfos"""

    install_var(clear, clear_all)


def install_var(clear, clear_all):
    """Install required folders in /var"""
    _check_root()

    hfoslog("Checking frontend library and cache directories",
            emitter='MANAGE')

    uid = pwd.getpwnam("hfos").pw_uid
    gid = grp.getgrnam("hfos").gr_gid

    # If these need changes, make sure they are watertight and don't remove
    # wanted stuff!
    target_paths = (
        '/var/www/challenges',  # For LetsEncrypt acme certificate challenges
        '/var/lib/hfos',
        '/var/cache/hfos',
        '/var/cache/hfos/tilecache',
        '/var/cache/hfos/rastertiles',
        '/var/cache/hfos/rastercache'
    )
    logfile = "/var/log/hfos.log"

    for item in target_paths:
        if os.path.exists(item):
            hfoslog("Path already exists: " + item, emitter='MANAGE')
            if clear_all or (clear and 'cache' in item):
                hfoslog("Cleaning up: " + item, emitter='MANAGE', lvl=warn)
                shutil.rmtree(item)

        if not os.path.exists(item):
            hfoslog("Creating path: " + item, emitter='MANAGE')
            os.mkdir(item)
            os.chown(item, uid, gid)

    # Touch logfile to make sure it exists
    open(logfile, "a").close()
    os.chown(logfile, uid, gid)

    hfoslog("Done: Install Var")


@install.command(short_help='install provisions')
@click.option('--provision', '-p', help="Specify a provision (default=install "
                                        "all)",
              default=None, metavar='<name>')
@click.option('--clear', help='Clears already existing collections (DANGER!)',
              is_flag=True, default=False)
@click.option('--overwrite', '-o', help='Overwrites existing provisions',
              is_flag=True, default=False)
@click.option('--dbhost', default=db_host_default, help=db_host_help)
def provisions(provision, dbhost, clear, overwrite):
    """Install default provisioning data"""

    install_provisions(provision, dbhost, clear, overwrite)


def install_provisions(provision, dbhost, clear=False, overwrite=False):
    """Install default provisioning data"""

    hfoslog("Installing HFOS default provisions", emitter='MANAGE')

    # from hfos.logger import verbosity, events
    # verbosity['console'] = verbosity['global'] = events
    from hfos import database
    database.initialize(dbhost)

    from hfos.provisions import provisionstore

    if provision is not None:
        if provision in provisionstore:
            hfoslog("Provisioning ", provision, emitter="MANAGE")
            provisionstore[provision](overwrite=overwrite, clear=clear)
        else:
            hfoslog("Unknown provision: ", provision, "\nValid provisions are",
                    list(provisionstore.keys()),
                    lvl=error,
                    emitter='MANAGE')
    else:
        for provision_name in provisionstore:
            hfoslog("Provisioning " + provision_name, emitter='MANAGE')
            provisionstore[provision_name](overwrite=overwrite, clear=clear)

    hfoslog("Done: Install Provisions")


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
            hfoslog("Problem during module installation: ", hfos_module, e,
                    type(e), exc=True, emitter='MANAGE', lvl=error)
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
        hfoslog('Installing module ', installable, emitter='MANAGE')
        if install_module(installable):
            success.append(installable)
        else:
            failed.append(installable)

    hfoslog('Installed modules: ', success, emitter='MANAGE')
    if len(failed) > 0:
        hfoslog('Failed modules: ', failed, emitter='MANAGE')
    hfoslog('Done: Install Modules', emitter='MANAGE')


@install.command(short_help='install systemd service')
def service():
    """Install systemd service configuration"""

    install_service()


def install_service():
    """Install systemd service configuration"""

    _check_root()

    hfoslog("Installing systemd service", emitter="MANAGE")

    launcher = os.path.realpath(__file__).replace('manage', 'launcher')
    executable = sys.executable + " " + launcher
    executable += " --dolog --logfile /var/log/hfos.log"
    executable += " --logfileverbosity 30 -q"

    definitions = {
        'executable': executable
    }

    write_template_file(os.path.join('dev/templates', service_template),
                        '/etc/systemd/system/hfos.service',
                        definitions)

    Popen([
        'systemctl',
        'enable',
        'hfos.service'
    ])

    hfoslog("Done: Install Service", emitter="MANAGE")


@install.command(short_help='install nginx configuration')
@click.option(
    '--hostname', default=None,
    help='Override public Hostname (FQDN) Default from active system '
         'configuration')
def nginx(hostname):
    """Install nginx configuration"""

    install_nginx(hostname)


def install_nginx(hostname=None):
    """Install nginx configuration"""

    _check_root()

    hfoslog("Installing nginx configuration", emitter="MANAGE")

    if hostname is None:
        try:
            config = _get_system_configuration()
            hostname = config.hostname
        except Exception as e:
            hfoslog('Exception:', e, type(e), exc=True, lvl=error)
            hfoslog("""Could not determine public fully qualified hostname!
Check systemconfig (see db view and db modify commands) or specify
manually with --hostname host.domain.tld

Using 'localhost' for now""", lvl=warn)
            hostname = 'localhost'

    definitions = {
        'server_public_name': hostname,
        'ssl_certificate': cert_file,
        'ssl_key': key_file,
        'host_url': 'http://127.0.0.1:8055/'
    }

    if distribution == 'DEBIAN':
        configuration_file = '/etc/nginx/sites-available/hfos.conf'
        configuration_link = '/etc/nginx/sites-enabled/hfos.conf'
    elif distribution == 'ARCH':
        configuration_file = '/etc/nginx/nginx.conf'
        configuration_link = None
    else:
        hfoslog('Unsure how to proceed, you may need to specify your '
                'distribution', lvl=error, emitter='MANAGE')
        return

    hfoslog('Writing nginx HFOS site definition')
    write_template_file(os.path.join('dev/templates', nginx_configuration),
                        configuration_file,
                        definitions)

    if configuration_link is not None:
        hfoslog('Enabling nginx HFOS site (symlink)')
        if not os.path.exists(configuration_link):
            os.symlink(configuration_file, configuration_link)

    hfoslog('Restarting nginx service')
    Popen([
        'systemctl',
        'restart',
        'nginx.service'
    ])

    hfoslog("Done: Install nginx configuration", emitter="MANAGE")


@install.command(short_help='create system user')
def system_user():
    """Install HFOS system user (hfos.hfos)"""

    install_system_user()
    hfoslog("Done: Setup User")


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
        hfoslog('Generating self signed (insecure) certificate/key '
                'combination')

        try:
            os.mkdir('/etc/ssl/certs/hfos')
        except FileExistsError:
            pass
        except PermissionError:
            hfoslog("Need root (e.g. via sudo) to generate ssl certificate")
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
                    hfoslog('Could not read old certificate to increment '
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

        hfoslog('Done: Install Cert')
    else:

        # # Account private key
        # openssl genrsa 4096 > account.key

        # # enerate a domain private key (if you haven't already)
        # openssl genrsa 4096 > domain.key

        # #for a single domain
        # openssl req -new -sha256 -key domain.key -subj "/CN=yoursite.com"
        # > domain.csr
        #
        # #for multiple domains (use this one if you want both
        # www.yoursite.com and yoursite.com)
        # openssl req -new -sha256 -key domain.key -subj "/" -reqexts SAN
        # -config <(cat /etc/ssl/openssl.cnf <(printf "[
        # SAN]\nsubjectAltName=DNS:yoursite.com,DNS:www.yoursite.com")) >
        # domain.csr

        # #run the script on your server
        # python acme_tiny.py --account-key ./account.key --csr ./domain.csr
        #  --acme-dir /var/www/challenges/ > ./signed.crt

        # #NOTE: For nginx, you need to append the Let's Encrypt
        # intermediate cert to your cert
        # wget -O - https://letsencrypt.org/certs/lets-encrypt-x3-cross
        # -signed.pem > intermediate.pem
        # cat signed.crt intermediate.pem > chained.pem

        # Renew certificate
        # #!/usr/bin/sh
        # python /path/to/acme_tiny.py --account-key /path/to/account.key
        # --csr /path/to/domain.csr --acme-dir /var/www/challenges/ >
        # /tmp/signed.crt || exit
        # wget -O - https://letsencrypt.org/certs/lets-encrypt-x3-cross
        # -signed.pem > intermediate.pem
        # cat /tmp/signed.crt intermediate.pem > /path/to/chained.pem
        # service nginx reload

        hfoslog('Not implemented yet. You can build your own certificate and '
                'store it in /etc/ssl/certs/hfos/server-cert.pem - it should '
                'be a certificate with key, as this is used server side and '
                'there is no way to enter a separate key.', lvl=error)


@install.command(short_help='build and install frontend')
@click.option('--dev', help="Use frontend development (./frontend) location",
              default=False, is_flag=True)
@click.option('--rebuild', help="Rebuild frontend before installation",
              default=False, is_flag=True)
def frontend(dev, rebuild):
    """Build and install frontend"""

    install_frontend(forcerebuild=rebuild, development=dev)


@install.command('all', short_help='install everything')
@click.option('--clear', help='Clears already existing cache '
                              'directories and data', is_flag=True,
              default=False)
def install_all(clear):
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

    It also builds and installs the HTML5 frontend."""

    _check_root()

    install_system_user()
    install_cert(selfsigned=True)

    install_var(clear=clear, clear_all=clear)
    install_modules(wip=False)
    install_provisions(provision=None, dbhost=db_host_default, clear=clear)
    install_docs(clear=clear)

    install_frontend(forcerebuild=True, development=True)
    install_service()
    install_nginx()

    hfoslog('Done')


cli.add_command(install)


@click.command(short_help='remove stuff in /var')
def uninstall():
    """Uninstall data and resource locations"""

    _check_root()

    response = _ask("This will delete all data of your HFOS installation! Type"
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
        hfoslog('No object uuid or filter specified.',
                lvl=error, emitter='manage')

    if obj is None:
        hfoslog('No object found',
                lvl=error, emitter='manage')
        return

    hfoslog('Object found, modifying', lvl=debug, emitter='manage')
    try:
        new_value = literal_eval(value)
    except ValueError:
        hfoslog('Interpreting value as string')
        new_value = str(value)

    obj._fields[field] = new_value
    obj.validate()
    hfoslog('Changed object validated', lvl=debug, emitter='manage')
    obj.save()
    hfoslog('Done')


@db.command(short_help='view objects')
@click.option("--schema", default=None)
@click.option("--uuid", default=None)
@click.option("--filter", default=None)
@click.pass_context
def view(ctx, schema, uuid, filter):
    """Show stored objects"""

    database = ctx.obj['db']

    if schema is None:
        hfoslog('No schema given. Read the help', lvl=warn, emitter='manage')
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
            hfoslog('No schema given. Read the help', lvl=warn, emitter='manage')
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

            hfoslog('Exception while validating:',
                    schema, e, type(e),
                    '\n\nFix this object and rerun validation!',
                    emitter='MANAGE', lvl=error)

    hfoslog('Done!', emitter='MANAGE')


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

    format = format.upper()

    if pretty:
        indent = 4
    else:
        indent = 0

    f = None

    if filename:
        try:
            f = open(filename, 'w')
        except (IOError, PermissionError) as e:
            hfoslog('Could not open output file for writing:', e, type(e), lvl=error)

    def output(what, convert=False):
        if convert:
            if format == 'JSON':
                data = json.dumps(what, indent=indent)
            else:
                data = ""
        else:
            data = what

        if not filename:
            print(data)
        else:
            f.write(data)

    database = ctx.obj['db']

    if schema is None:
        if all is False:
            hfoslog('No schema given. Read the help', lvl=warn, emitter='manage')
            return
        else:
            schemata = database.objectmodels.keys()
    else:
        schemata = [schema]

    all_items = {}

    for schema_item in schemata:
        model = database.objectmodels[schema_item]

        if uuid:
            obj = model.find({'uuid': uuid})
        elif filter:
            obj = model.find(literal_eval(filter))
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
            hfoslog('No schema given. Read the help', lvl=warn, emitter='manage')
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
            hfoslog('Would import', schema_total, 'items of', schema_item)
        all_items[schema_item] = items

    if dry:
        hfoslog('Would import', total, 'objects.')
    else:
        hfoslog('Importing', total, 'objects.')
        for schema_name, item_list in all_items.items():
            hfoslog('Importing', len(item_list), 'objects of type', schema_name)
            for item in item_list:
                item.save()


@db.command(short_help='find in object model fields')
@click.option("--search", help="Argument to search for in object model "
                               "fields",
              default=False, metavar='<text>')
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
                # hfoslog("Found queried fieldname in ", model)
        else:
            for field in fields:
                try:
                    if "type" in fields[field]:
                        # hfoslog(fields[field], field)
                        if fields[field]["type"] == search:
                            result.append((key, field))
                            # hfoslog("Found field", field, "in", model)
                except KeyError as e:
                    hfoslog("Field access error:", e, type(e), exc=True,
                            lvl=debug)

        if 'properties' in fields:
            # hfoslog('Sub properties checking:', fields['properties'])
            result.append(find(fields['properties'], search, by_type,
                               result, key=fields['name']))

        for field in fields:
            if 'items' in fields[field]:
                if 'properties' in fields[field]['items']:
                    # hfoslog('Sub items checking:', fields[field])
                    result.append(find(fields[field]['items'], search,
                                       by_type, result, key=field))
                else:
                    pass
                    # hfoslog('Items without proper definition!')

        return result

    if obj is not None:
        schema = database.objectmodels[obj]._schema
        result = find(schema, search, by_type, [], key="top")
        if result:
            # hfoslog(args.object, result)
            print(obj)
            pprint(result)
    else:
        for model, thing in database.objectmodels.items():
            schema = thing._schema

            result = find(schema, search, by_type, [], key="top")
            if result:
                print(model)
                # hfoslog(model, result)
                pprint(result)


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

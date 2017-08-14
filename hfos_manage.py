#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System - Dev Plugin
# =================================================
# Copyright (C) 2011-2016 riot <riot@c-base.org> and others.
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

from __future__ import print_function

import os
import sys
import shutil
import pwd
import grp
import click
import getpass

from click_didyoumean import DYMGroup
from click_repl import repl
from prompt_toolkit.history import FileHistory

from ast import literal_eval
from distutils.dir_util import copy_tree
from time import localtime, sleep
from uuid import uuid4
from collections import OrderedDict
from hashlib import sha512
from OpenSSL import crypto
from socket import gethostname
from pprint import pprint
from pymongo.errors import DuplicateKeyError

from hfos.ui.builder import install_frontend
from hfos.migration import make_migrations
from hfos.logger import verbose, debug, warn, error, critical, verbosity, \
    hfoslog
from dev.templates import write_template_file

# 2.x/3.x imports: (TODO: Simplify those, one 2x/3x ought to be enough)
try:
    input = raw_input  # NOQA
except NameError:
    pass

try:
    from subprocess import Popen, PIPE
except ImportError:
    from subprocess32 import Popen, PIPE  # NOQA

try:
    unicode  # NOQA
except NameError:
    unicode = str

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


def check_root():
    """Check if current user has root permissions"""

    if os.geteuid() != 0:
        hfoslog("Need root access to install. Use sudo!", lvl=error)
        hfoslog("If you installed into a virtual environment, don't forget to "
                "specify the interpreter binary for sudo, e.g:\n"
                "$ sudo /home/user/.virtualenv/hfos/bin/python3 "
                "hfos_manage.py")

        sys.exit(1)


def augment_info(info):
    """Fill out the template information"""

    info['description_header'] = "=" * len(info['description'])
    info['component_name'] = info['plugin_name'].capitalize()
    info['year'] = localtime().tm_year
    info['license_longtext'] = ''

    info['keyword_list'] = u""
    for keyword in info['keywords'].split(" "):
        print(keyword)
        info['keyword_list'] += u"\'" + str(keyword) + u"\', "
    print(info['keyword_list'])
    if len(info['keywor_dlist']) > 0:
        # strip last comma
        info['keyword_list'] = info['keyword_list'][:-2]

    return info


def construct_module(info, target):
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


def ask(question, default=None, data_type=str, show_hint=False):
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


def ask_questionnaire():
    """Asks questions to fill out a HFOS plugin template"""

    answers = {}
    print(info_header)
    pprint(questions.items())

    for question, default in questions.items():
        response = ask(question, default, type(default), show_hint=True)
        if type(default) == unicode and type(response) != str:
            response = response.decode('utf-8')
        answers[question] = response

    return answers


def ask_password():
    """Securely and interactively ask for a password"""

    password = "Foo"
    password_trial = ""

    while password != password_trial:
        password = getpass.getpass()
        password_trial = getpass.getpass(prompt="Repeat:")
        if password != password_trial:
            print("\nPasswords do not match!")

    return password


def get_credentials(username=None, password=None, dbhost=None):
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
        username = ask("Please enter username: ")
    else:
        username = username

    if password is None:
        password = ask_password()
    else:
        password = password

    try:
        password = password.encode('utf-8')
    except UnicodeDecodeError:
        password = password

    passhash = sha512(password)
    passhash.update(salt)

    return username, passhash.hexdigest()


def get_system_configuration():
    from hfos import database
    database.initialize()
    systemconfig = database.objectmodels['systemconfig'].find_one({
        'active': True
    })

    return systemconfig


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
        info = ask_questionnaire()
        pprint(info)
        done = ask('Is the above correct', default='y', data_type=bool)

    augmented_info = augment_info(info)

    hfoslog("Constructing module %(plugin_name)s" % info, emitter='MANAGE')
    construct_module(augmented_info, target)


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

    username, passhash = get_credentials(ctx.obj['username'],
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
        username = ask("Please enter username: ")
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

    username, passhash = get_credentials(ctx.obj['username'],
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
    check_root()

    def make_docs():
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
    check_root()

    hfoslog("Checking frontend library and cache directories",
            emitter='MANAGE')

    uid = pwd.getpwnam("hfos").pw_uid
    gid = grp.getgrnam("hfos").gr_gid

    # If these need changes, make sure they are watertight and don't remove
    # wanted stuff!
    target_paths = (
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
def modules():
    """Install the plugin modules"""

    install_modules()


def install_modules():
    def install_module(module):
        try:
            setup = Popen(
                [
                    sys.executable,
                    'setup.py',
                    'develop'
                ],
                cwd='modules/' + module + "/"
            )

            setup.wait()
        except Exception as e:
            hfoslog("Problem during module installation: ", module, e,
                    type(e), exc=True, emitter='MANAGE', lvl=error)
            return False
        return True

    installables = [
        # Poor man's dependency management, as long as the modules are
        # installed from local sources and they're not available on pypi,
        # which would handle real dependency management for us:
        'navdata',
        'robot',

        # Now all the rest:
        'alert',
        'busrepeater',
        'camera',
        'chat',
        'comms',
        'countables',
        'crew',
        'dash',
        # 'dev',
        'garden',
        'ldap',
        'library',
        'logbook',
        'maps',
        'mesh',
        'nmea',
        'polls',
        'project',
        'protocols',
        'shareables',
        'switchboard',
        'wiki'
    ]

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
    check_root()

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
    check_root()

    hfoslog("Installing nginx configuration", emitter="MANAGE")

    global key_file
    global cert_file
    global combined_file

    if hostname is None:
        try:
            config = get_system_configuration()
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

    configuration_file = '/etc/nginx/sites-available/hfos.conf'
    configuration_link = '/etc/nginx/sites-enabled/hfos.conf'

    hfoslog('Writing nginx HFOS site definition')
    write_template_file(os.path.join('dev/templates', nginx_configuration),
                        configuration_file,
                        definitions)

    hfoslog('Enabling nginx HFOS site')
    if not os.path.exists(configuration_link):
        os.symlink(configuration_file, configuration_link)

    hfoslog('Restarting nginx service')
    Popen([
        'systemctl',
        'restart',
        'nginx.service'
    ])

    hfoslog("Done: Install nginx configuration", emitter="MANAGE")


def install_system_user():
    check_root()

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
    sleep(2)


@install.command(short_help='create system user')
def system_user(*args):
    """Install HFOS system user (hfos.hfos)"""

    install_system_user()
    hfoslog("Done: Setup User")


def install_cert(selfsigned):
    check_root()

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

        global key_file
        global cert_file
        global combined_file

        def create_self_signed_cert():
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
        hfoslog('Not implemented yet. You can build your own certificate and '
                'store it in /etc/ssl/certs/hfos/server-cert.pem - it should '
                'be a certificate with key, as this is used server side and '
                'there is no way to enter a separate key.', lvl=error)


@install.command(short_help='install ssl certificate')
@click.option('--selfsigned', help="Use a self-signed certificate",
              default=True, is_flag=True)
def cert(selfsigned):
    """Install a local SSL certificate"""

    install_cert(selfsigned)


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

    It also builds and installs the HTML5 frontend."""

    check_root()

    install_system_user()
    install_cert(selfsigned=True)

    install_var(clear=clear, clear_all=clear)
    install_modules()
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

    check_root()

    response = ask("This will delete all data of your HFOS installation! Type"
                   "YES to continue:", default="N", show_hint=False)
    if response == 'YES':
        shutil.rmtree('/var/lib/hfos')
        shutil.rmtree('/var/cache/hfos')


cli.add_command(uninstall)


@db.command(short_help='modify fields of objects')
@click.option("--schema")
@click.option("--uuid")
@click.option("--filter")
@click.argument('field')
@click.argument('value')
@click.pass_context
def modify(ctx, schema, uuid, filter, field, value):
    database = ctx.obj['db']

    model = database.objectmodels[schema]

    if uuid:
        obj = model.find_one({'uuid': uuid})
    elif filter:
        obj = model.find_one(literal_eval(filter))
    else:
        hfoslog('No object uuid or filter specified. Read the help.',
                lvl=error, emitter='manage')

    hfoslog('Object found, modifying', lvl=debug, emitter='manage')
    obj._fields[field] = literal_eval(value)
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
        hfoslog('No object uuid or filter specified. Read the help.',
                lvl=warn, emitter='manage')
        return
    for item in obj:
        pprint(item._fields)


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
        search = ask("Enter search term")

    database = ctx.obj['db']

    def find(schema, search, by_type, result=[], key=""):
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
    prompt_kwargs = {
        'history': FileHistory('/tmp/.hfos-manage.history'),
    }
    print("""HFOS - Management Tool Interactive Prompt

Type -h for help, tab completion is available, hit Ctrl-D to quit.""")
    repl(click.get_current_context(), prompt_kwargs=prompt_kwargs)


if __name__ == '__main__':
    cli(obj={})

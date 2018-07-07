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
from hfos.provisions.base import provisionList

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

import grp
import pwd
import sys
import time
import networkx
from _socket import gethostname
from distutils.dir_util import copy_tree
from subprocess import Popen

import click
import os
import shutil
from OpenSSL import crypto
from click_didyoumean import DYMGroup

from hfos.logger import error, warn
from hfos.tool import _check_root, log, _get_system_configuration, _ask, run_process
from hfos.tool.templates import write_template_file
from hfos.tool.defaults import service_template, cert_file, key_file, distribution, nginx_configuration, combined_file

from hfos.ui.builder import install_frontend


@click.group(cls=DYMGroup)
@click.option('--port', help='Specify local HFOS port', default=8055)
@click.pass_context
def install(ctx, port):
    """Install various aspects of HFOS (GROUP)"""

    ctx.obj['port'] = port


@install.command(short_help='build and install docs')
@click.option('--clear', '--clear-target', help='Clears target documentation '
                                                'folders', default=False, is_flag=True)
@click.pass_context
def docs(ctx, clear_target):
    """Build and install documentation"""

    install_docs(str(ctx.obj['instance']), clear_target)


def install_docs(instance, clear_target):
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
        if clear_target:
            log("Cleaning up " + target, lvl=warn)
            shutil.rmtree(target)

    log("Copying docs to " + target)
    copy_tree(source, target)
    log("Done: Install Docs")


@install.command(short_help='create structures in /var')
@click.option('--clear', '--clear-target', help='Clears already existing cache '
                                                'directories', is_flag=True, default=False)
@click.option('--clear-all', help='Clears all already existing '
                                  'directories', is_flag=True, default=False)
@click.pass_context
def var(ctx, clear_target, clear_all):
    """Install variable data to /var/[lib,cache]/hfos"""

    install_var(str(ctx.obj['instance']), clear_target, clear_all)


def install_var(instance, clear_target, clear_all):
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
            if clear_all or (clear_target and 'cache' in item):
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
@click.option('--clear', '--clear-existing', help='Clears already existing collections (DANGER!)',
              is_flag=True, default=False)
@click.option('--overwrite', '-o', help='Overwrites existing provisions',
              is_flag=True, default=False)
@click.option('--list-provisions', '-l', help='Only list available provisions',
              is_flag=True, default=False)
def provisions(provision, clear_existing, overwrite, list_provisions):
    """Install default provisioning data"""

    install_provisions(provision, clear_existing, overwrite, list_provisions)


def install_provisions(provision, clear_provisions=False, overwrite=False, list_provisions=False):
    """Install default provisioning data"""

    log("Installing HFOS default provisions")

    # from hfos.logger import verbosity, events
    # verbosity['console'] = verbosity['global'] = events

    from hfos.provisions import build_provision_store

    provision_store = build_provision_store()

    def sort_dependencies(items):
        """Topologically sort the dependency tree"""

        g = networkx.DiGraph()

        for key, item in items:
            dependencies = item.get('dependencies', [])
            if isinstance(dependencies, str):
                dependencies = [dependencies]

            if key not in g:
                g.add_node(key)

            for link in dependencies:
                g.add_edge(key, link)

        if not networkx.is_directed_acyclic_graph(g):
            log('Cycles in provosioning dependency graph detected!', lvl=error)
            log('Involved provisions:', list(networkx.simple_cycles(g)), lvl=error)

        topology = list(networkx.algorithms.topological_sort(g))
        topology.reverse()

        log(topology, pretty=True)

        return topology

    if list_provisions:
        sort_dependencies(provision_store.items())
        exit()

    def provision_item(item):
        """Provision a single provisioning element"""

        method = item.get('method', provisionList)
        model = item.get('model')
        data = item.get('data')

        method(data, model, overwrite=overwrite, clear=clear_provisions)

    if provision is not None:
        if provision in provision_store:
            log("Provisioning ", provision, pretty=True)
            provision_item(provision_store[provision])
        else:
            log("Unknown provision: ", provision, "\nValid provisions are",
                list(provision_store.keys()),
                lvl=error,
                emitter='MANAGE')
    else:
        for name in sort_dependencies(provision_store.items()):
            log("Provisioning", name, pretty=True)
            provision_item(provision_store[name])

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

    # TODO: Sort module dependencies via topological sort or let pip do this in future.
    # # To get the module dependencies:
    # packages = {}
    # for provision_entrypoint in iter_entry_points(group='hfos.provisions',
    #                                               name=None):
    #     log("Found packages: ", provision_entrypoint.dist.project_name, lvl=warn)
    #
    #     _package_name = provision_entrypoint.dist.project_name
    #     _package = pkg_resources.working_set.by_key[_package_name]
    #
    #     print([str(r) for r in _package.requires()])  # retrieve deps from setup.py

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
    service_name = 'hfos-' + instance + '.service'

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
            configuration = _get_system_configuration(dbhost, dbname)
            hostname = configuration.hostname
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
                    certificate = open(cert_file, "rb").read()
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
            # noinspection PyPep8
            certificate.get_subject().O = "Hackerfleet"
            certificate.get_subject().OU = "Hackerfleet"
            certificate.get_subject().CN = gethostname()
            certificate.set_serial_number(serial)
            certificate.gmtime_adj_notBefore(0)
            certificate.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
            certificate.set_issuer(certificate.get_subject())
            certificate.set_pubkey(k)
            certificate.sign(k, b'sha512')

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
@click.option('--no-install', help="Do not install requirements",
              default=False, is_flag=True)
@click.option('--build-type', help="Specify frontend build type. Either dist(default) or build",
              default='dist')
@click.pass_context
def frontend(ctx, dev, rebuild, no_install, build_type):
    """Build and install frontend"""

    install_frontend(instance=ctx.obj['instance'],
                     forcerebuild=rebuild,
                     development=dev,
                     install=not no_install,
                     build_type=build_type)


@install.command('all', short_help='install everything')
@click.option('--clear', '--clear-all', help='Clears already existing cache directories and data', is_flag=True,
              default=False)
@click.pass_context
def install_all(ctx, clear_all):
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

    install_var(instance, clear_target=clear_all, clear_all=clear_all)
    install_modules(wip=False)
    install_provisions(provision=None, clear_provisions=clear_all)
    install_docs(instance, clear_target=clear_all)

    install_service(instance, dbhost, dbname, port)
    install_nginx(instance, dbhost, dbname, port)

    log('Done')


@click.command(short_help='remove stuff in /var')
def uninstall():
    """Uninstall data and resource locations"""

    _check_root()

    response = _ask("This will delete all data of your HFOS installations! Type"
                    "YES to continue:", default="N", show_hint=False)
    if response == 'YES':
        shutil.rmtree('/var/lib/hfos')
        shutil.rmtree('/var/cache/hfos')


@click.command(short_help='Manage updates')
@click.option('--no-restart', help='Do not restart service', is_flag=True, default=False)
@click.option('--no-rebuild', help='Do not rebuild frontend', is_flag=True, default=False)
@click.pass_context
def update(ctx, no_restart, no_rebuild):
    """Update a HFOS node"""

    # 0. (NOT YET! MAKE A BACKUP OF EVERYTHING)
    # 1. update repository
    # 2. update frontend repository
    # 3. (Not yet: update venv)
    # 4. rebuild frontend
    # 5. restart service

    instance = ctx.obj['instance']

    log('Pulling github updates')
    run_process('.', ['git', 'pull', 'origin', 'master'])
    run_process('./frontend', ['git', 'pull', 'origin', 'master'])

    if not no_rebuild:
        log('Rebuilding frontend')
        install_frontend(instance, forcerebuild=True, install=False, development=True)

    if not no_restart:
        log('Restaring service')
        if instance != 'hfos':
            instance = 'hfos-' + instance

        run_process('.', ['sudo', 'systemctl', 'restart', instance])

    log('Done')

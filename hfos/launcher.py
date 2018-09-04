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
from hfos import component

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""
Hackerfleet Operating System - Backend

Application
===========

See README.rst for Build/Installation and setup details.

URLs & Contact
==============

Mail: riot@c-base.org
IRC: #hackerfleet@irc.freenode.org

Project repository: http://github.com/hackerfleet/hfos
Frontend repository: http://github.com/hackerfleet/hfos-frontend


"""

import grp
import pwd
import sys

import click
import os
from circuits import Event
from circuits.web import Server, Static
from circuits.web.websockets.dispatcher import WebSocketsDispatcher

# from circuits.web.errors import redirect
# from circuits.app.daemon import Daemon
from hfos.component import handler, ConfigurableComponent
# from hfos.schemata.component import ComponentBaseConfigSchema
from hfos.database import initialize  # , schemastore
from hfos.events.system import populate_user_events
from hfos.logger import hfoslog, verbose, debug, warn, error, critical, \
    setup_root, verbosity, set_logfile
from hfos.debugger import cli_register_event
from hfos.ui.builder import install_frontend


# from pprint import pprint


class ready(Event):
    """Event fired to signal completeness of the local node's setup"""
    pass


class cli_components(Event):
    """List registered and running components"""
    pass


class cli_reload_db(Event):
    """Reload database and schemata (Dangerous!) WiP - does nothing right now"""
    pass


class cli_reload(Event):
    """Reload all components and data models"""
    pass


class cli_info(Event):
    """Provide information about the running instance"""
    pass


class cli_quit(Event):
    """Stop this instance

    Uses sys.exit() to quit.
    """
    pass


class cli_drop_privileges(Event):
    """Try to drop possible root privileges"""
    pass


def drop_privileges(uid_name='hfos', gid_name='hfos'):
    """Attempt to drop privileges and change user to 'hfos' user/group"""

    if os.getuid() != 0:
        hfoslog("Not root, cannot drop privileges", lvl=warn, emitter='CORE')
        return

    try:
        # Get the uid/gid from the name
        running_uid = pwd.getpwnam(uid_name).pw_uid
        running_gid = grp.getgrnam(gid_name).gr_gid

        # Remove group privileges
        os.setgroups([])

        # Try setting the new uid/gid
        os.setgid(running_gid)
        os.setuid(running_uid)

        # Ensure a very conservative umask
        # old_umask = os.umask(22)
        hfoslog('Privileges dropped', emitter='CORE')
    except Exception as e:
        hfoslog('Could not drop privileges:', e, type(e), exc=True, lvl=error, emitter='CORE')


class Core(ConfigurableComponent):
    """HFOS Core Backend Application"""
    # TODO: Move most of this stuff over to a new FrontendBuilder

    configprops = {
        'enabled': {
            'type': 'array',
            'title': 'Available modules',
            'description': 'Modules found and activatable by the system.',
            'default': [],
            'items': {'type': 'string'}
        },
        'components': {
            'type': 'object',
            'title': 'Components',
            'description': 'Component metadata',
            'default': {}
        },
        'frontendenabled': {
            'type': 'boolean',
            'title': 'Frontend enabled',
            'description': 'Option to toggle frontend activation',
            'default': True
        }
    }

    def __init__(self, args, **kwargs):
        super(Core, self).__init__("CORE", args, **kwargs)
        self.log("Starting system (channel ", self.channel, ")")

        self.insecure = args['insecure']
        self.quiet = args['quiet']
        self.development = args['dev']
        self.instance = args['instance']

        self.host = args['host']
        self.port = args['port']
        self.certificate = certificate = args['cert']

        if certificate:
            if not os.path.exists(certificate):
                self.log("SSL certificate usage requested but certificate "
                         "cannot be found!", lvl=error)
                sys.exit(17)  # TODO: Define exit codes

        self.frontendroot = os.path.abspath(os.path.dirname(os.path.realpath(
            __file__)) + "/../frontend")
        self.frontendtarget = os.path.join('/var/lib/hfos', self.instance, 'frontend')

        self.loadable_components = {}
        self.runningcomponents = {}

        self.frontendrunning = False

        self.static = None
        self.websocket = None

        self.component_blacklist = [  # 'camera',
            # 'logger',
            # 'debugger',
            'recorder',
            'playback',
            # 'sensors',
            # 'navdatasim'
            # 'ldap',
            # 'navdata',
            # 'nmeaparser',
            # 'objectmanager',
            # 'wiki',
            # 'clientmanager',
            # 'library',
            # 'nmeaplayback',
            # 'alert',
            # 'tilecache',
            # 'schemamanager',
            # 'chat',
            # 'debugger',
            # 'rcmanager',
            # 'auth',
            # 'machineroom'
        ]

        self.component_blacklist += args['blacklist']

        self.update_components()
        self._write_config()

        self.server = None

        if self.insecure:
            self.log("Not dropping privileges - this may be insecure!",
                     lvl=warn)

    @handler("started", channel="*")
    def ready(self, source):
        """All components have initialized, set up the component
        configuration schema-store, run the local server and drop privileges"""

        from hfos.database import configschemastore
        configschemastore[self.name] = self.configschema

        self._start_server()

        if not self.insecure:
            self._drop_privileges()

        self.fireEvent(cli_register_event('components', cli_components))
        self.fireEvent(cli_register_event('drop_privileges', cli_drop_privileges))
        self.fireEvent(cli_register_event('reload_db', cli_reload_db))
        self.fireEvent(cli_register_event('reload', cli_reload))
        self.fireEvent(cli_register_event('quit', cli_quit))
        self.fireEvent(cli_register_event('info', cli_info))

    @handler("frontendbuildrequest", channel="setup")
    def trigger_frontend_build(self, event):
        """Event hook to trigger a new frontend build"""

        from hfos.database import instance
        install_frontend(instance=instance,
                         forcerebuild=event.force,
                         install=event.install,
                         development=self.development
                         )

    @handler('cli_drop_privileges')
    def cli_drop_privileges(self, event):
        """Drop possible user privileges"""

        self.log('Trying to drop privileges', lvl=debug)
        self._drop_privileges()

    @handler('cli_components')
    def cli_components(self, event):
        """List all running components"""

        self.log('Running components: ', sorted(self.runningcomponents.keys()))

    @handler('cli_reload_db')
    def cli_reload_db(self, event):
        """Experimental call to reload the database"""

        self.log('This command is WiP.')

        initialize()

    @handler('cli_reload')
    def cli_reload(self, event):
        """Experimental call to reload the component tree"""

        self.log('Reloading all components.')

        self.update_components(forcereload=True)
        initialize()

        from hfos.debugger import cli_compgraph
        self.fireEvent(cli_compgraph())

    @handler('cli_quit')
    def cli_quit(self, event):
        """Stop the instance immediately"""

        self.log('Quitting on CLI request.')
        sys.exit()

    @handler('cli_info')
    def cli_info(self, event):
        """Provides information about the running instance"""

        self.log('Instance:', self.instance,
                 'Dev:', self.development,
                 'Host:', self.host,
                 'Port:', self.port,
                 'Insecure:', self.insecure,
                 'Frontend:', self.frontendtarget)

    def _start_server(self, *args):
        """Run the node local server"""

        self.log("Starting server", args)
        secure = self.certificate is not None
        if secure:
            self.log("Running SSL server with cert:", self.certificate)
        else:
            self.log("Running insecure server without SSL. Do not use without SSL proxy in production!", lvl=warn)

        try:
            self.server = Server(
                (self.host, self.port),
                secure=secure,
                certfile=self.certificate  # ,
                # inherit=True
            ).register(self)
        except PermissionError:
            self.log('Could not open (privileged?) port, check '
                     'permissions!', lvl=critical)

    def _drop_privileges(self, *args):
        self.log("Dropping privileges", lvl=debug)
        drop_privileges()

    # Moved to manage tool, maybe of interest later, though:
    #
    # @handler("componentupdaterequest", channel="setup")
    # def trigger_component_update(self, event):
    #     self.update_components(forcereload=event.force)

    def update_components(self, forcereload=False, forcerebuild=False,
                          forcecopy=True, install=False):
        """Check all known entry points for components. If necessary,
        manage configuration updates"""

        # TODO: See if we can pull out major parts of the component handling.
        # They are also used in the manage tool to instantiate the
        # component frontend bits.

        self.log("Updating components")
        components = {}

        if True:  # try:

            from pkg_resources import iter_entry_points

            entry_point_tuple = (
                iter_entry_points(group='hfos.base', name=None),
                iter_entry_points(group='hfos.sails', name=None),
                iter_entry_points(group='hfos.components', name=None)
            )

            for iterator in entry_point_tuple:
                for entry_point in iterator:
                    try:
                        name = entry_point.name
                        location = entry_point.dist.location
                        loaded = entry_point.load()

                        self.log("Entry point: ", entry_point,
                                 name,
                                 entry_point.resolve(), lvl=verbose)

                        self.log("Loaded: ", loaded, lvl=verbose)
                        comp = {
                            'package': entry_point.dist.project_name,
                            'location': location,
                            'version': str(entry_point.dist.parsed_version),
                            'description': loaded.__doc__
                        }

                        components[name] = comp
                        self.loadable_components[name] = loaded

                        self.log("Loaded component:", comp, lvl=verbose)

                    except Exception as e:
                        self.log("Could not inspect entrypoint: ", e,
                                 type(e), entry_point, iterator, lvl=error,
                                 exc=True)

                        # for name in components.keys():
                        #     try:
                        #         self.log(self.loadable_components[name])
                        #         configobject = {
                        #             'type': 'object',
                        #             'properties':
                        # self.loadable_components[name].configprops
                        #         }
                        #         ComponentBaseConfigSchema['schema'][
                        # 'properties'][
                        #             'settings'][
                        #             'oneOf'].append(configobject)
                        #     except (KeyError, AttributeError) as e:
                        #         self.log('Problematic configuration
                        # properties in '
                        #                  'component ', name, exc=True)
                        #
                        # schemastore['component'] = ComponentBaseConfigSchema

        # except Exception as e:
        #    self.log("Error: ", e, type(e), lvl=error, exc=True)
        #    return

        self.log("Checking component frontend bits in ", self.frontendroot,
                 lvl=verbose)

        # pprint(self.config._fields)
        diff = set(components) ^ set(self.config.components)
        if diff or forcecopy and self.config.frontendenabled:
            self.log("Old component configuration differs:", diff, lvl=debug)
            self.log(self.config.components, components, lvl=verbose)
            self.config.components = components
        else:
            self.log("No component configuration change. Proceeding.")

        if forcereload:
            self.log("Restarting all components.", lvl=warn)
            self._instantiate_components(clear=True)

    def _start_frontend(self, restart=False):
        """Check if it is enabled and start the frontend http & websocket"""

        self.log(self.config, self.config.frontendenabled, lvl=verbose)
        if self.config.frontendenabled and not self.frontendrunning or restart:
            self.log("Restarting webfrontend services on",
                     self.frontendtarget)

            self.static = Static("/",
                                 docroot=self.frontendtarget).register(
                self)
            self.websocket = WebSocketsDispatcher("/websocket").register(self)
            self.frontendrunning = True

    def _instantiate_components(self, clear=True):
        """Inspect all loadable components and run them"""

        if clear:
            import objgraph
            from copy import deepcopy
            from circuits.tools import kill
            from circuits import Component
            for comp in self.runningcomponents.values():
                self.log(comp, type(comp), isinstance(comp, Component), pretty=True)
                kill(comp)
            # removables = deepcopy(list(self.runningcomponents.keys()))
            #
            # for key in removables:
            #     comp = self.runningcomponents[key]
            #     self.log(comp)
            #     comp.unregister()
            #     comp.stop()
            #     self.runningcomponents.pop(key)
            #
            #     objgraph.show_backrefs([comp],
            #                            max_depth=5,
            #                            filter=lambda x: type(x) not in [list, tuple, set],
            #                            highlight=lambda x: type(x) in [ConfigurableComponent],
            #                            filename='backref-graph_%s.png' % comp.uniquename)
            #     del comp
            # del removables
            self.runningcomponents = {}

        self.log('Not running blacklisted components: ',
                 self.component_blacklist,
                 lvl=debug)

        running = set(self.loadable_components.keys()).difference(
            self.component_blacklist)
        self.log('Starting components: ', sorted(running))
        for name, componentdata in self.loadable_components.items():
            if name in self.component_blacklist:
                continue
            self.log("Running component: ", name, lvl=verbose)
            try:
                if name in self.runningcomponents:
                    self.log("Component already running: ", name,
                             lvl=warn)
                else:
                    runningcomponent = componentdata()
                    runningcomponent.register(self)
                    self.runningcomponents[name] = runningcomponent
            except Exception as e:
                self.log("Could not register component: ", name, e,
                         type(e), lvl=error, exc=True)

    def started(self, component):
        """Sets up the application after startup."""

        self.log("Running.")
        self.log("Started event origin: ", component, lvl=verbose)
        populate_user_events()

        from hfos.events.system import AuthorizedEvents
        self.log(len(AuthorizedEvents), "authorized event sources:",
                 list(AuthorizedEvents.keys()), lvl=debug)

        self._instantiate_components()
        self._start_frontend()
        self.fire(ready(), "hfosweb")


def construct_graph(args):
    """Preliminary HFOS application Launcher"""

    app = Core(args)

    setup_root(app)

    if args['debug']:
        from circuits import Debugger
        hfoslog("Starting circuits debugger", lvl=warn, emitter='GRAPH')
        dbg = Debugger().register(app)
        # TODO: Make these configurable from modules, navdata is _very_ noisy
        # but should not be listed _here_
        dbg.IgnoreEvents.extend([
            "read", "_read", "write", "_write",
            "stream_success", "stream_complete",
            "serial_packet", "raw_data", "stream",
            "navdatapush", "referenceframe",
            "updateposition", "updatesubscriptions",
            "generatevesseldata", "generatenavdata", "sensordata",
            "reset_flood_offenders", "reset_flood_counters",  # Flood counters
            "task_success", "task_done",  # Thread completion
            "keepalive"  # IRC Gateway
        ])

    hfoslog("Beginning graph assembly.", emitter='GRAPH')

    if args['drawgraph']:
        from circuits.tools import graph

        graph(app)

    if args['opengui']:
        import webbrowser
        # TODO: Fix up that url:
        webbrowser.open("http://%s:%i/" % (args['host'], args['port']))

    hfoslog("Graph assembly done.", emitter='GRAPH')

    return app


@click.command()
@click.option("-p", "--port", help="Define port for server", type=int,
              default=8055)
@click.option("--host", help="Define hostname for server", type=str,
              default='127.0.0.1')
@click.option("--certificate", "--cert", '-c', help="Certificate file path",
              type=str, default=None)
@click.option("--dbhost", help="Define hostname for database server",
              type=str, default='127.0.0.1:27017')
@click.option('--dbname', default='hfos', help='Define name of database (default: hfos)',
              metavar='<name>')
@click.option("--profile", help="Enable profiler", is_flag=True)
@click.option("--opengui", help="Launch webbrowser for GUI inspection after "
                                "startup", is_flag=True)
@click.option("--drawgraph", help="Draw a snapshot of the component graph "
                                  "after construction", is_flag=True)
@click.option("--quiet", "-q", help="Suppress console output", is_flag=True)
@click.option("--log", help="Define console log level (0-100)", type=int,
              default=20)
@click.option("--logfileverbosity", help="Define file log level (0-100)",
              type=int, default=20)
@click.option("--logfilepath", default="/var/log/", help="Logfile path")
@click.option("--dolog", help="Write to logfile", is_flag=True)
@click.option("--livelog", help="Log to in memory structure as well", is_flag=True)
@click.option("--debug", help="Run circuits debugger", is_flag=True)
@click.option("--dev", help="Run development server", is_flag=True, default=True)
@click.option('--instance', default='default', help='Define name of instance',
              metavar='<name>')
@click.option("--insecure", help="Keep privileges - INSECURE", is_flag=True)
@click.option("--norun", help="Only assemble system, do not run", is_flag=True)
@click.option("--blacklist", "-b", help="Blacklist a component", multiple=True, default=[])
def launch(run=True, **args):
    """Bootstrap basics, assemble graph and hand over control to the Core
    component"""

    verbosity['console'] = args['log'] if not args['quiet'] else 100
    verbosity['global'] = min(args['log'], args['logfileverbosity'])
    verbosity['file'] = args['logfileverbosity'] if args['dolog'] else 100
    set_logfile(args['logfilepath'], args['instance'])

    if args['livelog'] is True:
        from hfos import logger
        logger.live = True

    hfoslog("Running with Python", sys.version.replace("\n", ""),
            sys.platform, lvl=debug, emitter='CORE')
    hfoslog("Interpreter executable:", sys.executable, emitter='CORE')
    if args['cert'] is not None:
        hfoslog("Warning! Using SSL without nginx is currently not broken!",
                lvl=critical, emitter='CORE')

    hfoslog("Initializing database access", emitter='CORE', lvl=debug)
    initialize(args['dbhost'], args['dbname'], args['instance'])

    server = construct_graph(args)
    if run and not args['norun']:
        server.run()

    return server

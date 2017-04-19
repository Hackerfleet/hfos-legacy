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

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from circuits.web.websockets.dispatcher import WebSocketsDispatcher
from circuits.web import Server, Static
# from circuits.app.daemon import Daemon
from circuits import handler, reprhandler, Event

from hfos.ui.builder import install_frontend
# from hfos.schemata.component import ComponentBaseConfigSchema
from hfos.database import initialize  # , schemastore
from hfos.component import ConfigurableComponent
from hfos.logger import hfoslog, verbose, debug, warn, error, critical, \
    setup_root, verbosity, hilight, set_logfile

import argparse
import sys
import pwd
import grp
import os

# from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


class ready(Event):
    pass


def drop_privileges(uid_name='hfos', gid_name='hfos'):
    if os.getuid() != 0:
        hfoslog("Not root, cannot drop privileges. Probably opening "
                "the web port failed as well", lvl=warn, emitter='CORE')
        return

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
        'frontendtarget': {
            'type': 'string',
            'title': 'Frontend Target',
            'description': 'Frontend deployment directory',
            'default': '/var/lib/hfos/frontend'
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

        self.insecure = args.insecure
        self.quiet = args.quiet
        self.development = args.dev

        self.host = args.host
        self.port = args.port
        self.certificate = certificate = args.certificate

        if certificate:
            if not os.path.exists(certificate):
                self.log("SSL certificate usage requested but certificate "
                         "cannot be found!", lvl=error)
                sys.exit(17)  # TODO: Define exit codes

        self.frontendroot = os.path.abspath(os.path.dirname(os.path.realpath(
            __file__)) + "/../frontend")

        self.loadable_components = {}
        self.runningcomponents = {}

        self.frontendrunning = False

        self.static = None
        self.websocket = None

        self.component_blacklist = [  # 'camera',
            'logger',
            # 'debugger'
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

        self.update_components()
        self._write_config()

        self.server = None

        if self.insecure:
            self.log("Not dropping privileges - this may be insecure!",
                     lvl=warn)

    @handler("started", channel="*")
    def ready(self, source):
        from hfos.database import configschemastore
        configschemastore[self.name] = self.configschema

        self._start_server()

        if not self.insecure:
            self._drop_privileges()

    @handler("frontendbuildrequest", channel="setup")
    def trigger_frontend_build(self, event):
        install_frontend(forcerebuild=event.force,
                         install=event.install,
                         development=self.development
                         )

    def _start_server(self, *args):
        self.log("Starting server", args, lvl=warn)
        secure = self.certificate is not None
        if secure:
            self.log("Running SSL server with cert:", self.certificate)
        else:
            self.log("Running insecure server without SSL!", lvl=warn)

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
        self.log("Dropping privileges", args, lvl=warn)
        drop_privileges()

    # Moved to manage tool, maybe of interest later, though:
    #
    # @handler("componentupdaterequest", channel="setup")
    # def trigger_component_update(self, event):
    #     self.update_components(forcereload=event.force)

    def update_components(self, forcereload=False, forcerebuild=False,
                          forcecopy=True, install=False):

        # TODO: See if we can pull out major parts of the component handling.
        # They are also used in the manage tool to instantiate the
        # component frontend bits.

        hfoslog("Updating components")
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

                        hfoslog("Entry point: ", entry_point,
                                name,
                                entry_point.resolve(), lvl=verbose)

                        hfoslog("Loaded: ", loaded, lvl=verbose)
                        comp = {
                            'location': location,
                            'version': str(entry_point.dist.parsed_version),
                            'description': loaded.__doc__
                        }

                        components[name] = comp
                        self.loadable_components[name] = loaded

                        hfoslog("Loaded component:", comp, lvl=verbose)

                    except Exception as e:
                        hfoslog("Could not inspect entrypoint: ", e,
                                type(e), entry_point, iterator, lvl=error,
                                exc=True)

                        # for name in components.keys():
                        #     try:
                        #         hfoslog(self.loadable_components[name])
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
                        #         hfoslog('Problematic configuration
                        # properties in '
                        #                  'component ', name, exc=True)
                        #
                        # schemastore['component'] = ComponentBaseConfigSchema

        # except Exception as e:
        #    hfoslog("Error: ", e, type(e), lvl=error, exc=True)
        #    return

        hfoslog("Checking component frontend bits in ", self.frontendroot,
                lvl=verbose)

        # pprint(self.config._fields)
        diff = set(components) ^ set(self.config.components)
        if diff or forcecopy and self.config.frontendenabled:
            hfoslog("Old component configuration differs:", diff, lvl=debug)
            hfoslog(self.config.components, components, lvl=verbose)
            self.config.components = components
        else:
            hfoslog("No component configuration change. Proceeding.")

        if forcereload:
            hfoslog("Restarting all components.", lvl=warn)
            self._instantiate_components(clear=True)

    def _start_frontend(self, restart=False):
        self.log(self.config, self.config.frontendenabled, lvl=verbose)
        if self.config.frontendenabled and not self.frontendrunning \
                or restart:
            self.log("Restarting webfrontend services on",
                     self.config.frontendtarget)

            self.static = Static("/",
                                 docroot=self.config.frontendtarget).register(
                self)
            self.websocket = WebSocketsDispatcher("/websocket").register(self)
            self.frontendrunning = True

    def _instantiate_components(self, clear=True):
        if clear:
            for comp in self.runningcomponents.values():
                comp.unregister()
                comp.stop()
                del comp
            self.runningcomponents = {}

        self.log('Not running blacklisted components: ',
                 self.component_blacklist,
                 lvl=debug)

        running = set(self.loadable_components.keys()).difference(
            self.component_blacklist)
        self.log('Starting components: ', running)
        for name, componentdata in self.loadable_components.items():
            if name in self.component_blacklist:
                continue
            self.log("Running component: ", name, lvl=debug)
            try:
                if name in self.runningcomponents:
                    self.log("Component already running: ", name,
                             lvl=warn)
                else:
                    runningcomponent = componentdata().register(self)
                    self.runningcomponents[name] = runningcomponent
            except Exception as e:
                self.log("Could not register component: ", name, e,
                         type(e), lvl=error, exc=True)

    def started(self, component):
        """Sets up the application after startup."""
        self.log("Running.")
        self.log("Started event origin: ", component, lvl=verbose)

        self._instantiate_components()
        self._start_frontend()
        self.fire(ready(), "hfosweb")


def construct_graph(args):
    """Preliminary HFOS application Launcher"""

    app = Core(args)

    setup_root(app)

    if args.debug:
        from circuits import Debugger
        hfoslog("Starting circuits debugger", lvl=warn, emitter='GRAPH')
        dbg = Debugger().register(app)
        dbg.IgnoreEvents.extend(["write", "_write", "streamsuccess"])

    hfoslog("Beginning graph assembly.", emitter='GRAPH')

    if args.drawgraph:
        from circuits.tools import graph

        graph(app)

    if args.opengui:
        import webbrowser

        webbrowser.open("http://%s:%i/" % (args.host, args.port))

    hfoslog("Graph assembly done.", emitter='GRAPH')

    return app


def launch(run=True):
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Define port for server",
                        type=int, default=80)
    parser.add_argument("--host", help="Define hostname for server",
                        type=str, default='0.0.0.0')
    parser.add_argument("--certificate",
                        "--cert", '-c',
                        help="Certificate file path",
                        type=str, default=None)
    parser.add_argument("--dbhost", help="Define hostname for database server",
                        type=str, default='127.0.0.1:27017')
    parser.add_argument("--profile", help="Enable profiler",
                        action="store_true")
    parser.add_argument("--opengui", help="Launch webbrowser for GUI "
                                          "inspection after startup",
                        action="store_true")
    parser.add_argument("--drawgraph", help="Draw a snapshot of the "
                                            "component graph "
                                            "after construction",
                        action="store_true")
    parser.add_argument("--quiet", "-q", help="Suppress console output",
                        action="store_true")
    parser.add_argument("--log", help="Define console log level (0-100)",
                        type=int, default=20)
    parser.add_argument("--logfileverbosity",
                        help="Define file log level (0-100)",
                        type=int, default=20)
    parser.add_argument("--logfile", help="Logfile path",
                        default='/tmp/hfos.log')
    parser.add_argument("--dolog", help="Write to logfile",
                        action="store_true")
    parser.add_argument("--debug", help="Run circuits debugger",
                        action="store_true")

    parser.add_argument("--dev", help="Run development server",
                        action="store_true")

    parser.add_argument("--insecure", help="Keep privileges - INSECURE",
                        action="store_true")

    args = parser.parse_args()
    # pprint(args)

    verbosity['console'] = args.log if not args.quiet else 100
    verbosity['global'] = min(args.log, args.logfileverbosity)
    verbosity['file'] = args.logfileverbosity if args.dolog else 100
    set_logfile(args.logfile)

    hfoslog("Running with Python", sys.version.replace("\n", ""),
            sys.platform, lvl=debug, emitter='CORE')
    hfoslog("Interpreter executable:", sys.executable, emitter='CORE')

    hfoslog("Initializing database access", emitter='CORE')
    initialize(args.dbhost)

    server = construct_graph(args)
    if run:
        server.run()

    return server

"""
Hackerfleet Operating System - Backend

Application
===========

See README.rst for Build/Installation and setup details.

URLs & Contact
==============

Hackerfleet Homepage: http://hackerfleet.org
Mail: info@hackerfleet.org
IRC: #hackerfleet@irc.freenode.org

Project repository: http://github.com/hackerfleet/hfos
Frontend repository: http://github.com/hackerfleet/hfos-frontend

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from circuits.web.websockets.dispatcher import WebSocketsDispatcher
from circuits.web import Server, Static
from circuits import handler, Timer, Event
from hfos.schemata.component import ComponentBaseConfigSchema
from hfos.database import schemastore
from hfos.component import ConfigurableComponent
from hfos.logger import hfoslog, verbose, debug, warn, error, critical, \
    setup_root
import sys
from glob import glob
import os
from subprocess import Popen, TimeoutExpired
from shutil import copy
import os, pwd, grp

# from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

hfoslog("Running with Python", sys.version.replace("\n", ""),
        sys.platform, lvl=debug, emitter='CORE')
hfoslog("Interpreter executable:", sys.executable, emitter='CORE')


class dropPrivs(Event):
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


def copytree(root_src_dir, root_dst_dir, hardlink=True):
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                if hardlink:
                    hfoslog('Removing frontend link:', dst_file,
                            emitter='BUILDER', lvl=verbose)
                    os.remove(dst_file)
                else:
                    hfoslog('Overwriting frontend file:', dst_file,
                            emitter='BUILDER', lvl=verbose)

            hfoslog('Hardlinking ', src_file, dst_dir, emitter='BUILDER',
                    lvl=verbose)
            try:
                if hardlink:
                    os.link(src_file, dst_file)
                else:
                    copy(src_file, dst_dir)
            except PermissionError as e:
                hfoslog("Could not create target %s for frontend:" % (
                    'link' if hardlink else 'copy'),
                        dst_dir, e, emitter='BUILDER', lvl=error)
            except Exception as e:
                hfoslog("Error during", 'link' if hardlink else 'copy',
                        "creation:", type(e), e, emitter='BUILDER', lvl=error)

            hfoslog('Done linking', root_dst_dir, emitter='BUILDER',
                    lvl=verbose)


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

    def __init__(self, args):
        super(Core, self).__init__("CORE")
        self.log("Booting. ", self.channel)

        self.args = args

        self.frontendroot = os.path.abspath(os.path.dirname(os.path.realpath(
            __file__)) + "/../frontend")

        self.loadable_components = {}
        self.runningcomponents = {}

        self.frontendrunning = False

        self.banlist = [  # 'camera',
            'logger'
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

        self.updateComponents()
        self._writeConfig()

        self.server = Server((args.host, args.port)).register(self)

        if self.args.insecure is not True:
            self.log("Setting five second timer to drop privileges.",
                     lvl=debug)
            Timer(5, dropPrivs()).register(self)
        else:
            self.log("Not dropping privileges - this may be insecure!",
                 lvl=warn)

    @handler("dropPrivs")
    def dropPrivileges(self, *args):
        self.log("Dropping privileges", lvl=warn)
        drop_privileges()

    @handler("frontendbuildrequest", channel="setup")
    def triggerFrontendBuild(self, event):
        self.updateComponents(forcerebuild=event.force, install=event.install)

    @handler("componentupdaterequest", channel="setup")
    def triggerComponentUpdate(self, event):
        self.updateComponents(forcereload=event.force)

    # TODO: Installation of frontend requirements is currently disabled
    def updateComponents(self, forcereload=False, forcerebuild=False,
                         forcecopy=True, install=False):
        self.log("Updating components")
        components = {}

        try:

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
                            'location': location,
                            'version': str(entry_point.dist.parsed_version),
                            'description': loaded.__doc__
                        }

                        frontend = os.path.join(location, 'frontend')
                        self.log("Checking component frontend parts: ",
                                 frontend, lvl=verbose)
                        if os.path.isdir(
                                frontend) and frontend != self.frontendroot:
                            comp['frontend'] = frontend

                        components[name] = comp
                        self.loadable_components[name] = loaded

                        self.log("Loaded component:", comp, lvl=verbose)

                    except Exception as e:
                        self.log("Could not inspect entrypoint: ", e,
                                 type(e), entry_point, iterator, lvl=error,
                                 exc=True)
                        return

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


        except Exception as e:
            self.log("Error: ", e, type(e), lvl=error, exc=True)
            return

        self.log("Checking component frontend bits in ", self.frontendroot,
                 lvl=verbose)

        # pprint(self.config._fields)
        diff = set(components) ^ set(self.config.components)
        if diff or forcecopy and self.config.frontendenabled:
            self.log("Old component configuration differs:", diff, lvl=debug)
            self.log(self.config.components, components, lvl=verbose)
            self.config.components = components

            self.updateFrontends(install)

            if forcerebuild:
                self.rebuildFrontend()

                # We have to find a way to detect if we need to rebuild (and
                # possibly wipe) stuff. This maybe the case, when a frontend
                #  has
                # been updated.
        else:
            self.log("No component configuration change. Proceeding.")

        if forcereload:
            self.log("Restarting all components. Good luck.", lvl=warn)
            self.instantiateComponents(clear=True)

    def updateFrontends(self, install=True):
        self.log("Checking unique frontend locations: ",
                 self.config.components, lvl=debug)

        importlines = []
        modules = []

        for name, component in self.config.components.items():
            if 'frontend' in component:
                origin = component['frontend']

                target = os.path.join(self.frontendroot, 'src', 'components',
                                      name)
                target = os.path.normpath(target)

                if install:
                    reqfile = os.path.join(origin, 'requirements.txt')

                    if os.path.exists(reqfile):
                        self.log("Installing package dependencies", lvl=debug)
                        with open(reqfile, 'r') as f:
                            cmdline = ["npm", "install"]
                            for line in f.readlines():
                                cmdline.append(line.replace("\n", ""))

                            self.log("Running", cmdline, lvl=verbose)
                            npminstall = Popen(cmdline, cwd=self.frontendroot)
                            out, err = npminstall.communicate()
                            try:
                                npminstall.wait(timeout=60)
                            except TimeoutExpired:
                                self.log("Timeout during package "
                                         "install", lvl=error)
                                return

                            self.log("Frontend installing done: ", out,
                                     err, lvl=debug)

                # if target in ('/', '/boot', '/usr', '/home', '/root',
                # '/var'):
                #    self.log("Unsafe frontend deletion target path, "
                #            "NOT proceeding! ", target, lvl=critical)

                self.log("Copying:", origin, target, lvl=debug)

                copytree(origin, target)

                for modulefilename in glob(target + '/*.module.js'):
                    modulename = os.path.basename(modulefilename).split(
                        ".module.js")[0]
                    line = u"import {s} from './components/{p}/{" \
                           u"s}.module';\n" \
                           u"modules.push({s});\n".format(s=modulename, p=name)
                    if not modulename in modules:
                        importlines += line
                        modules.append(modulename)

        main = ""
        with open(os.path.join(self.frontendroot, 'src', 'main.tpl.js'),
                  "r") as f:
            main = "".join(f.readlines())

        parts = main.split("/* COMPONENT SECTION */")
        if len(parts) != 3:
            self.log("Frontend loader seems damaged! Please check!",
                     lvl=critical)
            return

        try:
            with open(os.path.join(self.frontendroot, 'src', 'main.js'),
                      "w") as f:
                f.write(parts[0])
                f.write("/* COMPONENT SECTION:BEGIN */\n")
                for line in importlines:
                    f.write(line)
                f.write("/* COMPONENT SECTION:END */\n")
                f.write(parts[2])
        except Exception as e:
            self.log("Error during frontend package info writing. Check "
                     "permissions! ", e, lvl=error)

    def rebuildFrontend(self):
        self.log("Starting frontend build.", lvl=warn)
        npmbuild = Popen(["npm", "run", "build"], cwd=self.frontendroot)
        out, err = npmbuild.communicate()
        try:
            npmbuild.wait(timeout=60)
        except TimeoutExpired:
            self.log("Timeout during build", lvl=error)
            return

        self.log("Frontend build done: ", out, err, lvl=debug)
        copytree(os.path.join(self.frontendroot, 'build'),
                 self.config.frontendtarget, hardlink=False)
        copytree(os.path.join(self.frontendroot, 'assets'),
                 os.path.join(self.config.frontendtarget, 'assets'),
                 hardlink=False)
        self.startFrontend()
        self.log("Frontend deployed")

    def startFrontend(self, restart=False):
        self.log(self.config, self.config.frontendenabled)
        if self.config.frontendenabled and not self.frontendrunning \
                or restart:
            self.log("Restarting webfrontend services.")
            self.log(self.config)
            self.static = Static("/",
                                 docroot=self.config.frontendtarget).register(
                self)
            self.websocket = WebSocketsDispatcher("/websocket").register(self)
            self.frontendrunning = True

    def instantiateComponents(self, clear=True):
        if clear:
            for comp in self.runningcomponents.values():
                comp.unregister()
                comp.stop()
                del comp
            self.runningcomponents = {}

        for name, componentdata in self.loadable_components.items():
            if name in self.banlist:
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
                         type(e), lvl=error)  # ().register(self)

    def started(self, component):
        """Sets up the application after startup."""
        self.log("Running.")
        self.log("Started event origin: ", component, lvl=verbose)

        self.instantiateComponents()
        self.startFrontend()


def registerComponent(self):
    hfoslog("Registration called!")


def construct_graph(args):
    """Preliminary HFOS application Launcher"""

    app = Core(args)

    setup_root(app)

    # if dodebug:
    # from circuits import Debugger

    # dbg = Debugger()
    # dbg.IgnoreEvents.extend(["write", "_write", "streamsuccess"])

    # HFDebugger(root=server).register(server)

    hfoslog("Beginning graph assembly.", emitter='GRAPH')

    if args.drawgraph:
        from circuits.tools import graph

        graph(app)

    if args.opengui:
        import webbrowser

        webbrowser.open("http://%s:%i/" % (args.host, args.port))

    hfoslog("Graph assembly done.", emitter='GRAPH')

    return app


def launch(args):
    server = construct_graph(args)
    server.run()

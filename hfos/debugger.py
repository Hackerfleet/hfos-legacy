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


Module: Debugger
================

Debugger overlord


"""

import json
from uuid import uuid4

from circuits.core.events import Event
from circuits.core.handlers import reprhandler
from circuits.io import stdin

from hfos.component import ConfigurableComponent, handler
from hfos.events.client import send
from hfos.events.system import frontendbuildrequest, componentupdaterequest, \
    logtailrequest, debugrequest
from hfos.logger import hfoslog, critical, error, warn, debug, verbose, verbosity

try:
    import objgraph
except ImportError:
    objgraph = None

try:
    from guppy import hpy
except ImportError:
    hpy = None


class clicommand(Event):
    """Event to execute previously registered CLI event hooks"""

    def __init__(self, cmd, cmdargs, *args, **kwargs):
        super(clicommand, self).__init__(*args, **kwargs)
        self.cmd = cmd
        self.args = cmdargs


class cli_register_event(Event):
    """Event to register new command line interface event hooks"""

    def __init__(self, cmd, thing, *args, **kwargs):
        super(cli_register_event, self).__init__(*args, **kwargs)
        self.cmd = cmd
        self.thing = thing


class cli_help(Event):
    """Display this command reference

    Additional arguments:
        -v      Add detailed information about hook events in list

        command Show complete documentation of a hook command
    """
    pass


class cli_errors(Event):
    """Display errors in the live log"""
    pass


class cli_log_level(Event):
    """Adjust log level

    Argument:
        [int]   New logging level (0-100)
    """
    pass


class cli_compgraph(Event):
    """Draw current component graph"""
    pass


class HFDebugger(ConfigurableComponent):
    """
    Handles various debug requests.
    """
    configprops = {
        'notificationusers': {
            'type': 'array',
            'title': 'Notification receivers',
            'description': 'Users that should be notified about exceptions.',
            'default': [],
            'items': {'type': 'string'}
        }
    }
    channel = "hfosweb"

    def __init__(self, root=None, *args):
        super(HFDebugger, self).__init__("DBG", *args)

        if not root:
            from hfos.logger import root
            self.root = root
        else:
            self.root = root

        if hpy is not None:
            # noinspection PyCallingNonCallable
            self.heapy = hpy()
        else:
            self.log("Cannot use heapy. guppy package missing?", lvl=warn)

        if objgraph is None:
            self.log("Cannot use objgraph.", lvl=warn)

        try:
            self.fireEvent(cli_register_event('errors', cli_errors))
            self.fireEvent(cli_register_event('log_level', cli_log_level))
            self.fireEvent(cli_register_event('compgraph', cli_compgraph))
        except AttributeError:
            pass  # We're running in a test environment and root is not yet running

        self.log("Started. Notification users: ", self.config.notificationusers)

    @handler("cli_errors")
    def cli_errors(self, *args):
        self.log('All errors since startup:')
        from hfos.logger import LiveLog
        for logline in LiveLog:
            if logline[1] >= error:
                self.log(logline, pretty=True)

    @handler("cli_log_level")
    def cli_log_level(self, *args):
        new_level = int(args[0])
        self.log('Adjusting logging level to', new_level)

        verbosity['global'] = new_level
        verbosity['console'] = new_level
        verbosity['file'] = new_level

    @handler("exception", channel="*", priority=100.0)
    def _on_exception(self, error_type, value, traceback,
                      handler=None, fevent=None):

        try:
            s = []

            if handler is None:
                handler = ""
            else:
                handler = reprhandler(handler)

            msg = "ERROR"
            msg += "{0:s} ({1:s}) ({2:s}): {3:s}\n".format(
                handler, repr(fevent), repr(error_type), repr(value)
            )

            s.append(msg)
            s.extend(traceback)
            s.append("\n")

            self.log("\n".join(s), lvl=critical)

            alert = {
                'component': 'hfos.alert.manager',
                'action': 'notify',
                'data': {
                    'type': 'danger',
                    'message': "\n".join(s),
                    'title': 'Exception Monitor'
                }
            }
            for user in self.config.notificationusers:
                self.fireEvent(send(None, alert, username=user,
                                    sendtype='user'))

        except Exception as e:
            self.log("Exception during exception handling: ", e, type(e),
                     lvl=critical)

    @handler('cli_compgraph')
    def cli_compgraph(self, event):
        self.log('Drawing component graph')
        from circuits.tools import graph

        graph(self)
        self._drawgraph()

    def _drawgraph(self):
        objgraph.show_backrefs([self.root],
                               max_depth=5,
                               filter=lambda x: type(x) not in [list, tuple, set],
                               highlight=lambda x: type(x) in [ConfigurableComponent],
                               filename='backref-graph.png')
        self.log("Backref graph written.", lvl=critical)

    @handler(debugrequest)
    def debugrequest(self, event):
        """Handler for client-side debug requests"""
        try:
            self.log("Event: ", event.__dict__, lvl=critical)

            if event.data == "storejson":
                self.log("Storing received object to /tmp", lvl=critical)
                fp = open('/tmp/hfosdebugger_' + str(
                    event.user.useruuid) + "_" + str(uuid4()), "w")
                json.dump(event.data, fp, indent=True)
                fp.close()
            if event.data == "memdebug":
                self.log("Memory hogs:", lvl=critical)
                objgraph.show_most_common_types(limit=20)
            if event.data == "growth":
                self.log("Memory growth since last call:", lvl=critical)
                objgraph.show_growth()
            if event.data == "graph":
                self._drawgraph()
            if event.data == "exception":
                class TestException(BaseException):
                    """Generic exception to test exception monitoring"""

                    pass

                raise TestException
            if event.data == "heap":
                self.log("Heap log:", self.heapy.heap(), lvl=critical)
            if event.data == "buildfrontend":
                self.log("Sending frontend build command")

                self.fireEvent(frontendbuildrequest(force=True), "setup")
            if event.data == "logtail":
                self.fireEvent(logtailrequest(event.user, None, None,
                                              event.client), "logger")
            if event.data == "trigger_anchorwatch":
                from hfos.anchor.anchorwatcher import cli_trigger_anchorwatch
                self.fireEvent(cli_trigger_anchorwatch())

        except Exception as e:
            self.log("Exception during debug handling:", e, type(e),
                     lvl=critical)


class CLI(ConfigurableComponent):
    """
    Command Line Interface support
    """

    configprops = {}

    def __init__(self, *args):
        super(CLI, self).__init__("CLI", *args)

        self.hooks = {}

        self.log("Started")
        stdin.register(self)
        self.fire(cli_register_event('help', cli_help))

    @handler("read", channel="stdin")
    def stdin_read(self, data):
        """read Event (on channel ``stdin``)
        This is the event handler for ``read`` events specifically from the
        ``stdin`` channel. This is triggered each time stdin has data that
        it has read.
        """

        data = data.strip().decode("utf-8")
        self.log("Incoming:", data, lvl=verbose)

        if len(data) == 0:
            self.log('Use /help to get a list of enabled cli hooks')
            return

        if data[0] == "/":
            cmd = data[1:]
            args = []
            if ' ' in cmd:
                cmd, args = cmd.split(' ', maxsplit=1)
                args = args.split(' ')
            if cmd in self.hooks:
                self.log('Firing hooked event:', cmd, args, lvl=debug)
                self.fireEvent(self.hooks[cmd](*args))
            # TODO: Move these out, so we get a simple logic here
            elif cmd == 'frontend':
                self.log("Sending %s frontend rebuild event" %
                         ("(forced)" if 'force' in args else ''))
                self.fireEvent(
                    frontendbuildrequest(force='force' in args,
                                         install='install' in args),
                    "setup")
            elif cmd == 'backend':
                self.log("Sending backend reload event")
                self.fireEvent(componentupdaterequest(force=False), "setup")
            else:
                self.log('Unknown Command:', cmd, '. Use /help to get a list of enabled '
                                                  'cli hooks')

    @handler('cli_help')
    def cli_help(self, *args):
        if len(args) == 0 or args[0].startswith('-'):
            self.log('Registered CLI hooks:')
            # TODO: Use std_table for a pretty table
            command_length = 5
            object_length = 5
            for hook in self.hooks:
                command_length = max(len(hook), command_length)
                object_length = max(len(str(self.hooks[hook])), object_length)

            if '-v' not in args:
                object_length = 0

            for hook in sorted(self.hooks):
                self.log('/%s %s: %s' % (
                    hook.ljust(command_length),
                    (" - " + str(self.hooks[hook]) if object_length != 0 else "").ljust(object_length),
                    str(self.hooks[hook].__doc__).split('\n', 1)[0]

                ))
        else:
            self.log('Help for command', args[0], ':')
            self.log(self.hooks[args[0]].__doc__)

    @handler('cli_register_event')
    def register_event(self, event):
        """Registers a new command line interface event hook as command"""

        self.log('Registering event hook:', event.cmd, event.thing,
                 pretty=True, lvl=verbose)
        self.hooks[event.cmd] = event.thing

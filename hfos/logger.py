#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2015 riot <riot@hackerfleet.org> and others.
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

"""
Module: Logger
==============

HFOS own logger to avoid namespace clashes etc. Comes with some fancy
functions.

Log Levels
----------

verbose = 5
debug = 10
info = 20
warn = 30
error = 40
critical = 50
off = 100

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from circuits import Component, handler
from circuits.core import Event
# from uuid import uuid4
# import json


import time
import os
import sys
import inspect
import six

root = None

events = 2
network = 4
verbose = 5
debug = 10
info = 20
warn = 30
error = 40
critical = 50
hilight = 60
off = 100
lvldata = {
    events: ['EVENT', '\033[1:36m'],
    verbose: ['VERB', '\033[1;30m'],
    network: ['NET', '\033[1;34m'],
    debug: ['DEBUG', '\033[1;97m'],
    info: ['INFO', '\033[1;92m'],
    warn: ['WARN', '\033[1;91m'],
    error: ['ERROR', '\033[1;31;43m'],
    critical: ['CRIT', '\033[1;33;41m'],
    hilight: ['HILIGHT', '\033[1;4;30;106m']
}

terminator = '\033[0m'

count = 0

logfile = "/var/log/hfos/service.log"

console = debug

verbosity = {'global': console,
             'file': off,
             'system': error,
             'console': console
             }

mute = []
solo = []

start = time.time()


class logevent(Event):
    """
    Generates a new log event to be logged to the system log

    :param msg: Description of event
    :param severity:  Severity of event
    :param args:
    """

    def __init__(self, timestamp, severity, emitter, sourceloc, content,
                 *args):
        super(logevent, self).__init__(*args)
        self.timestamp = timestamp
        self.severity = severity
        self.emitter = emitter
        self.sourceloc = sourceloc
        self.content = content

    def __str__(self):
        return str(self.content)


class send(Event):
    """Send a packet to a known client by UUID"""

    def __init__(self, uuid, packet, sendtype="client",
                 raw=False, username=None, *args):
        """

        :param uuid: Unique User ID of known connection
        :param packet: Data packet to transmit to client
        :param args: Further Args
        """
        super(send, self).__init__(*args)

        if uuid == None and username == None:
            hfoslog("[SEND-EVENT] No recipient (uuid/name) given!", lvl=warn)
        self.uuid = uuid
        self.packet = packet
        self.username = username
        self.sendtype = sendtype
        self.raw = raw


def ismuted(what):
    """
    Checks if a logged event is to be muted for debugging purposes.

    Also goes through the solo list - only items in there will be logged!

    :param what:
    :return:
    """
    global mute, solo

    state = False

    for item in solo:
        if item not in what:
            state = True
        else:
            state = False
            break

    for item in mute:
        if item in what:
            state = True
            break

    return state


def setup_root(newroot):
    """
    Sets up the root component, so the logger knows where to send logging
    signals.

    :param newroot:
    """
    global root

    root = newroot


def hfoslog(*what, **kwargs):
    """Logs all args except "lvl" which is used to determine the incident
    log level.
    :param kwargs: Debug message level
    :param what: Loggable objects (i.e. they have a string representation)
    """

    # TODO: Filter out log levels BEFORE doing _anything_ here
    if 'lvl' in kwargs:
        lvl = kwargs['lvl']
        if lvl < verbosity['global']:
            return
    else:
        lvl = info

    if 'emitter' in kwargs:
        emitter = kwargs['emitter']
    else:
        emitter = 'UNKNOWN'

    if 'exc' in kwargs:
        exception = True
    else:
        exception = False

    global count

    output = None
    count += 1

    now = time.time() - start

    line_no = None
    callee = None

    if verbosity['global'] <= debug:
        # Automatically log the current function details.

        if not 'sourceloc' in kwargs:

            # Get the previous frame in the stack, otherwise it would
            # be this function!!!
            func = inspect.currentframe().f_back.f_code
            # Dump the message + the name of this function to the log.

            if exception:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                line_no = exc_tb.tb_lineno
                lvl = error
            else:
                line_no = func.co_firstlineno

            callee = "[%.10s@%s:%i]" % (
                func.co_name,
                func.co_filename,
                line_no
            )
        else:
            callee = kwargs['sourceloc']

    msg = "[%s] : %5s : %.5f : %3i : [%5s]" % (time.asctime(),
                                               lvldata[lvl][0],
                                               now,
                                               count,
                                               emitter)

    content = ""

    if callee:
        msg += "%-60s" % callee

    for thing in what:
        content += " "
        content += str(thing)

    msg += content

    if ismuted(msg):
        return

    if len(msg) > 1000:
        msg = msg[:1000]

    if lvl >= verbosity['file']:
        try:
            f = open(logfile, "a")
            f.write(msg + '\n')
            f.flush()
            f.close()
        except IOError:
            print("Can't open logfile for writing!")
            # sys.exit(23)

    if lvl >= verbosity['console']:
        output = str(msg)
        if six.PY3:
            output = lvldata[lvl][1] + output + terminator
        print(output)
    if lvl >= verbosity['system'] and root and output:
        root.fire(logevent(now, lvl, emitter, callee, content), "logger")

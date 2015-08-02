#!/usr/bin/env python3
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

HFOS own logger to avoid namespace clashes etc. Comes with some fancy functions.

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
from circuits.tools import findroot

from uuid import uuid4

import json


import time
import sys
import inspect
import six

root = None

events = 4
verbose = 5
debug = 10
info = 20
warn = 30
error = 40
critical = 50
off = 100

lvldata = {4: ['EVENTS', '\033[1:97m'],
           5: ['VERBOSE', '\033[1;97m'],
           10: ['DEBUG', '\033[1;97m'],
           20: ['INFO', '\033[1;92m'],
           30: ['WARN', '\033[1;94m'],
           40: ['ERROR', '\033[1;91m'],
           50: ['CRITICAL', '\033[1;95m'],
           }
terminator = '\033[0m'

count = 0

logfile = "/var/log/hfos/service.log"
verbosity = {'global': events,
             'file': off,
             'console': debug,
             }

mute = []
solo = []

start = time.time()


class LogEvent(Event):
    def __init__(self, msg, severity, *args):
        super(LogEvent, self).__init__(*args)

        self.msg = msg
        self.severity = severity

    def __str__(self):
        return str(self.msg)

def isMuted(what):
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
    global root

    root = newroot

def hfoslog(*what, **kwargs):
    """Logs all args except "lvl" which is used to determine the incident log level.
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

    global count

    output = None
    count += 1

    now = time.time() - start
    msg = "[%s] : %8s : %.5f : %i :" % (time.asctime(),
                                        lvldata[lvl][0],
                                        now,
                                        count)
    if verbosity['global'] <= debug:
        # Automatically log the current function details.

        # Get the previous frame in the stack, otherwise it would
        # be this function!!!
        func = inspect.currentframe().f_back.f_code
        # Dump the message + the name of this function to the log.
        callee = "[%.10s@%s:%i]" % (
            func.co_name,
            func.co_filename,
            func.co_firstlineno
        )
        msg += "%-60s" % callee

    for thing in what:
        msg += " "
        msg += str(thing)

    if isMuted(msg):
        return

    if lvl >= verbosity['file']:
        try:
            f = open(logfile, "a")
            f.write(msg)
            f.flush()
            f.close()
        except IOError:
            print("Can't open logfile for writing!")
            sys.exit(23)

    if lvl >= verbosity['console']:
        output = str(msg)
        if six.PY3:
            output = lvldata[lvl][1] + output + terminator
        print(output)
    if root and output:
        root.fire(LogEvent(str(output), lvl), "logger")


class Logger(Component):
    """
    System logger

    Handles all the logging aspects.

    """

    channels = "logger"

    def __init__(self, *args):
        super(Logger, self).__init__(*args)

        hfoslog("[LOGGER] Started.")

    @handler("LogEvent")
    def LogEvent(self, event):
        pass

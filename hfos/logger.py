#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Hackerfleet Technology Demonstrator
# =====================================================================
# Copyright (C) 2011-2014 riot <riot@hackerfleet.org> and others.
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


import time
import sys
import inspect

verbose = 5
debug = 10
info = 20
warn = 30
error = 40
critical = 50
off = 100

lvldata = {5: ['VERBOSE', '\033[1;97m'],
           10: ['DEBUG', '\033[1;97m'],
           20: ['INFO', '\033[1;92m'],
           30: ['WARN', '\033[1;94m'],
           40: ['ERROR', '\033[1;91m'],
           50: ['CRITICAL', '\033[1;95m'],
           }

count = 0

logfile = "/var/log/hfos/service.log"
verbosity = {'global': verbose,
             'file': off,
             'console': debug}

start = time.time()


def hfoslog(*what, **kwargs):
    if 'lvl' in kwargs:
        lvl = kwargs['lvl']
        if lvl < verbosity['global']:
            return
    else:
        lvl = info

    global count
    global start
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
        print(lvldata[lvl][1], str(msg), '\033[0m')

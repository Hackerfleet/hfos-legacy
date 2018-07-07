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

import getpass
import sys

import hashlib
import os

from hfos.logger import hfoslog, error
# 2.x/3.x imports: (TODO: Simplify those, one 2x/3x ought to be enough)
from hfos.tool.defaults import db_host_default, db_host_help, db_host_metavar, db_default, db_help, db_metavar

try:
    # noinspection PyUnresolvedReferences,PyShadowingBuiltins
    input = raw_input  # NOQA
except NameError:
    pass

try:
    from subprocess import Popen, PIPE
except ImportError:
    # noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
    from subprocess32 import Popen, PIPE  # NOQA


def log(*args, **kwargs):
    """Log as Emitter:MANAGE"""

    kwargs.update({'emitter': 'MANAGE', 'frame_ref': 2})
    hfoslog(*args, **kwargs)


def _check_root():
    """Check if current user has root permissions"""

    if os.geteuid() != 0:
        log("Need root access to install. Use sudo!", lvl=error)
        log("If you installed into a virtual environment, don't forget to "
            "specify the interpreter binary for sudo, e.g:\n"
            "$ sudo /home/user/.virtualenv/hfos/bin/python3 "
            "hfos_manage.py")

        sys.exit(1)


def run_process(cwd, args):
    """Executes an external process via subprocess.Popen"""
    try:
        process = Popen(args, cwd=cwd)

        process.wait()
    except Exception as e:
        log('Uh oh, the teapot broke again! Error:', e, type(e), lvl=error)


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
        log('No systemconfig or it is without a salt! '
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


def _get_system_configuration(dbhost, dbname):
    from hfos import database
    database.initialize(dbhost, dbname)
    systemconfig = database.objectmodels['systemconfig'].find_one({
        'active': True
    })

    return systemconfig


def _ask(question, default=None, data_type='str', show_hint=False):
    """Interactively ask the user for data"""

    data = default

    if data_type == 'bool':
        data = None
        default_string = "Y" if default else "N"

        while data not in ('Y', 'J', 'N', '1', '0'):
            data = input("%s? [%s]: " % (question, default_string)).upper()

            if data == '':
                return default

        return data in ('Y', 'J', '1')

    elif data_type in ('str', 'unicode'):
        if show_hint:
            msg = "%s? [%s] (%s): " % (question, default, data_type)
        else:
            msg = question

        data = input(msg)

        if len(data) == 0:
            data = default
    elif data_type == 'int':
        if show_hint:
            msg = "%s? [%s] (%s): " % (question, default, data_type)
        else:
            msg = question

        data = input(msg)

        if len(data) == 0:
            data = int(default)
        else:
            data = int(data)

    return data



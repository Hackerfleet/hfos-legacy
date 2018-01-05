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

"""Testsuite runner"""

import sys
# noinspection PyUnresolvedReferences
from types import ModuleType
from os.path import abspath, dirname
from subprocess import Popen, STDOUT


def importable(module_name):
    """Safely try to import a module"""

    try:
        m = __import__(module_name, globals(), locals())
        return type(m) is ModuleType
    except ImportError:
        return False


def main():
    """Run all tests with coverage output"""

    cmd = ["py.test", "-r", "fsxX", "--durations=10", "--ignore=tmp"]

    if importable("pytest_cov"):
        cmd.append("--cov=hfos")
        cmd.append("--no-cov-on-fail")
        cmd.append("--cov-report=html")

    cmd.append(dirname(abspath(__file__)))

    raise SystemExit(Popen(cmd, stdout=sys.stdout, stderr=STDOUT).wait())


if __name__ == "__main__":
    main()

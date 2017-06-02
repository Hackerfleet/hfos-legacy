#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2017 Heiko 'riot' Weinen <riot@c-base.org> and others.
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

__author__ = "Heiko 'riot' Weinen"
__license__ = "GPLv3"

"""
Hackerfleet Operating System - Backend

Test HFOS Launcher
==================



"""

from circuits import Manager
import pytest
from hfos import logger
from time import sleep

from pprint import pprint

m = Manager()
component = pytest.TestComponent()
component.register(m)


def test_component_logging():
    """Throws an exception inside the system and tests if the debugger picks
    it up correctly"""

    m.start()

    logger.live = True
    component.log('FOOBAR')

    lastlog = "".join(logger.LiveLog[-1:])

    assert "FOOBAR" in lastlog


def test_script_logging():
    logger.live = True

    logger.hfoslog('FOOBAR')

    lastlog = "".join(logger.LiveLog[-1:])

    assert "FOOBAR" in lastlog

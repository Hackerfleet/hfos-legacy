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

Test HFOS Basic Provisioning
============================



"""

import pytest
from uuid import uuid4
import hfos.logger as logger


def test_uniquename():
    """Tests uniquename functionality of HFOS base components"""

    a = pytest.TestComponent()
    b = pytest.TestComponent()

    pytest.clean_test_components()
    assert a.uniquename != b.uniquename


def test_named():
    """Tests named HFOS base components"""

    a = pytest.TestComponent(uniquename="BERTRAM")
    pytest.clean_test_components()

    assert a.uniquename == "BERTRAM"


def test_configschema():
    """Tests if ConfigurableComponents obtain a configuration schema"""

    c = pytest.TestComponent()
    pytest.clean_test_components()

    assert type(c.configschema) == dict
    assert 'schema' in c.configschema
    assert 'properties' in c.configschema['schema']


def test_config_uuid():
    """Tests if ConfigurableComponents configurations get an UUID assigned"""

    c = pytest.TestComponent()
    pytest.clean_test_components()

    assert type(c.config.uuid) == str


def test_config_storage():
    """Should test if components store their configuration properly"""
    pass


def test_config_change():
    """Should test, if changed configurations are stored to the database"""
    pass


def test_component_log():
    """Tests if a component logs correctly"""

    c = pytest.TestComponent()
    unique = str(uuid4())

    log = logger.LiveLog
    logger.live = True

    c.log(unique)
    pytest.clean_test_components()

    assert unique in str(log)

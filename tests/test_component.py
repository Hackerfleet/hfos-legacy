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
Hackerfleet Operating System - Backend

Test HFOS Basic Provisioning
============================



"""

import pytest
from uuid import uuid4
from circuits import Manager
import hfos.logger as logger
import hfos.component


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


def test_unique_warning():
    """Test for uniqueness of generated components"""

    log = logger.LiveLog
    logger.live = True

    c = pytest.TestComponent(uniquename='FOO')
    d = pytest.TestComponent(uniquename='FOO')

    pytest.clean_test_components()

    assert "Unique component added twice: " in str(log)


def test_unregister():
    """Test if component cleanly unregisters from namespace"""

    name = "test_unregister"
    m = Manager()

    c = pytest.TestComponent(uniquename=name)
    c.register(m)

    assert name in pytest.TestComponent.names

    c.unregister()

    assert name not in pytest.TestComponent.names


def test_write_none_config():
    """Test if writing a non existing configuration fails"""

    log = logger.LiveLog
    logger.live = True

    c = pytest.TestComponent()
    c.config = None
    c._write_config()

    pytest.clean_test_components()

    assert "Unable to write non existing configuration" in str(log)


def test_configurable_controller():
    """Test instantiation of the configurable controller"""

    c = hfos.component.ConfigurableController()

    assert type(c) == hfos.component.ConfigurableController


def test_example_component():
    """Test instantiation of the example component"""

    c = hfos.component.ExampleComponent()

    assert type(c) == hfos.component.ExampleComponent

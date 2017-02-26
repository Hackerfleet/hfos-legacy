"""
Hackerfleet Operating System - Backend

Test HFOS Basic Provisioning
============================


:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.component import ConfigurableComponent, ExampleComponent
from uuid import uuid4
import hfos.logger as logger

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


def test_uniquename():
    """Tests uniquename functionality of HFOS base components"""

    a = ConfigurableComponent()
    b = ConfigurableComponent()

    assert a.uniquename != b.uniquename

def test_named():
    """Tests named HFOS base components"""

    a = ConfigurableComponent(uniquename="BERTRAM")

    assert a.uniquename == "BERTRAM"

def test_configschema():
    """Tests if ConfigurableComponents obtain a configuration schema"""

    c = ConfigurableComponent()

    assert type(c.configschema) == dict
    assert 'schema' in c.configschema
    assert 'properties' in c.configschema['schema']


def test_component_log():
    """Tests if a component logs correctly"""

    c = ConfigurableComponent()
    unique = str(uuid4())

    log = logger.LiveLog
    logger.live = True

    c.log(unique)

    assert unique in str(log)

def test_example_component():
    """Instantiates the example component, which doesn't do much, anyway"""

    c = ExampleComponent()

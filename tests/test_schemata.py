"""
Hackerfleet Operating System - Backend

Test HFOS Basic Provisioning
============================


:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

import pytest
from hfos.database import schemastore

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

schemata = schemastore.keys()

@pytest.mark.parametrize('schemaname', schemata)
def test_definition(schemaname):
    """Tests base object user provisioning"""

    schemadefinition = schemastore[schemaname]

    assert 'schema' in schemadefinition
    assert 'id' in schemadefinition['schema']

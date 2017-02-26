"""
Hackerfleet Operating System - Backend

Test HFOS Basic Provisioning
============================


:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.database import _build_schemastore_new

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

def test_invalid_schema_store_generation():
    """Tests for refusal of store generation with an invalid schema"""

    schemadefinition = {
        'foobar': 'qux'
    }

    schemastore = _build_schemastore_new()

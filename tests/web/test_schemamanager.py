"""
Hackerfleet Operating System - Backend

Test HFOS Schemamanager
=======================


:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from hfos.web.schemamanager import SchemaManager


def test_():
    sm = SchemaManager()
    assert type(sm) == SchemaManager

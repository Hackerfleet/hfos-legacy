"""
Hackerfleet Operating System - Backend

Test HFOS Basic Provisioning
============================


:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


def test_version_string():
    """Tests if a version exists and if it is a string"""

    from hfos.version import version

    assert type(version) == str

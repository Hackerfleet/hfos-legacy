"""
Hackerfleet Operating System - Backend

Test HFOS Basic Provisioning
============================


:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""


__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


def test_systemconfig_provision():
    """Tests correct instantiation"""

    from hfos.provisions.system import provision

    assert callable(provision)

def test_user_provision():
    """Tests base object user provisioning"""

    from hfos.provisions.user import provision

    assert callable(provision)

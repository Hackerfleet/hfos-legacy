"""
Hackerfleet Operating System - Backend

Test HFOS Launcher
==================


:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.database import initialize
from hfos.launcher import Core

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

initialize()  # Set up database access for testing once


def test_launcher():
    """Tests if the Core Launcher can be instantiated"""

    # Use a non privileged port for testing, until that part can be removed
    # from Core

    core = Core(port=8123)

    assert type(core) == Core

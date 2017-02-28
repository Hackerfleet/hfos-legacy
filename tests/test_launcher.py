"""
Hackerfleet Operating System - Backend

Test HFOS Launcher
==================


:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.launcher import Core

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

class args_mock(object):
    def __init__(self):
        object.__init__(self)
        self.insecure = False
        self.quiet = False
        self.dev = False
        self.port = 80
        self.host = '127.0.0.1'
        self.certificate = None


def test_launcher():
    """Tests if the Core Launcher can be instantiated"""

    # Use a non privileged port for testing, until that part can be removed
    # from Core

    args = args_mock()
    core = Core(args)

    assert type(core) == Core

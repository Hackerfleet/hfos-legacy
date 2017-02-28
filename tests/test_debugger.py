"""
Hackerfleet Operating System - Backend

Test HFOS Launcher
==================


:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from circuits import Manager
import pytest
from hfos.debugger import HFDebugger
from hfos.events.system import debugrequest
from hfos.ui.clientobjects import User
from hfos import logger
from time import sleep

from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

m = Manager()
hfd = HFDebugger().register(m)


def test_instantiate():
    """Tests correct instantiation"""

    assert type(hfd) == HFDebugger


def test_exception_monitor():
    """Throws an exception inside the system and tests if the debugger picks
    it up correctly"""

    m.start()

    logger.live = True
    hfd.log('FOOBAR')

    m.fireEvent(debugrequest(User(None, None, None), 'exception', None, None),
                "hfosweb")

    sleep(0.2)
    lastlog = "".join(logger.LiveLog[-1:])

    assert "ERROR" in lastlog


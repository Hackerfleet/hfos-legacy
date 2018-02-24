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

import pytest

import sys
import threading
import collections
from time import sleep
from collections import deque

from circuits.core.manager import TIMEOUT
from circuits import handler, BaseComponent, Debugger, Manager

from hfos.component import ConfigurableComponent
from hfos.schemata.component import ComponentConfigSchemaTemplate
from warmongo import model_factory

"""Basic Test suite bits and pieces"""


class TestComponent(ConfigurableComponent):
    """Very basic testing component"""

    configprops = {
        'test': {'type': 'string'}
    }


class Watcher(BaseComponent):
    """Watches for incoming events"""

    def __init__(self, *args, **kwargs):
        super(Watcher).__init__(*args, **kwargs)
        self.events = deque()
        self._lock = threading.Lock()

    @handler(channel="*", priority=999.9)
    def _on_event(self, event, *args, **kwargs):
        with self._lock:
            self.events.append(event)

    def clear(self):
        """Reset caught events"""

        self.events.clear()

    def wait(self, name, channel=None, timeout=6.0):
        """Linger and wait for specified incoming events"""

        for i in range(int(timeout / TIMEOUT)):
            with self._lock:
                for event in self.events:
                    if event.name == name and event.waitingHandlers == 0:
                        if (channel is None) or (channel in event.channels):
                            return True
            sleep(TIMEOUT)
        else:
            return False


class Flag(object):
    """Flag object for Watcher component"""
    status = False
    event = None


def call_event_from_name(manager, event, event_name, *channels):
    """Fire a named event and wait for a specified response"""

    fired = False
    value = None
    for r in manager.waitEvent(event_name):
        if not fired:
            fired = True
            value = manager.fire(event, *channels)
        sleep(0.1)
    return value


def call_event(manager, event, *channels):
    """Simply fire and forget a specified event"""

    return call_event_from_name(manager, event, event.name, *channels)


class WaitEvent(object):
    """Simple component substitute that waits for a specified Event"""

    def __init__(self, manager, name, channel=None, timeout=1.0):
        if channel is None:
            channel = getattr(manager, "channel", None)

        self.timeout = timeout
        self.manager = manager

        flag = Flag()

        @handler(name, channel=channel)
        def on_event(self, event):
            """An event has been received"""

            flag.status = True
            flag.event = event

        self.handler = self.manager.addHandler(on_event)
        self.flag = flag

    def wait(self):
        """Wait for the (upon instantiation) specified timeout for an event"""
        try:
            for i in range(int(self.timeout / TIMEOUT)):
                if self.flag.status:
                    return self.flag.event
                sleep(TIMEOUT)
        finally:
            self.manager.removeHandler(self.handler)


def wait_for(obj, attr, value=True, timeout=3.0):
    """Wait until timeout or an object acquires a specified attribute"""

    from circuits.core.manager import TIMEOUT
    for i in range(int(timeout / TIMEOUT)):
        if isinstance(value, collections.Callable):
            if value(obj, attr):
                return True
        elif getattr(obj, attr) == value:
            return True
        sleep(TIMEOUT)


@pytest.fixture
def manager(request):
    """Component testing manager/fixture"""

    manager = Manager()

    def finalizer():
        """Stop the testing"""

        manager.stop()

    request.addfinalizer(finalizer)

    waiter = WaitEvent(manager, "started")
    manager.start()
    assert waiter.wait()

    if request.config.option.verbose:
        verbose = True
    else:
        verbose = False

    Debugger(events=verbose).register(manager)

    return manager


@pytest.fixture
def watcher(request, manager):
    """Fixture that cleans up after unregistering"""

    watcher = Watcher().register(manager)

    def finalizer():
        """Setup the manager and wait for completion, then unregister"""

        waiter = WaitEvent(manager, "unregistered")
        watcher.unregister()
        waiter.wait()

    request.addfinalizer(finalizer)

    return watcher


def clean_test_components():
    """Removes test-generated component data"""

    print("Removing test components...")
    for item in model_factory(ComponentConfigSchemaTemplate).find({
        'componentclass': 'TestComponent'
    }):
        item.delete()


@pytest.hookimpl()
def pytest_unconfigure(config):
    """Clear test generated data after test completion"""
    clean_test_components()


def pytest_namespace():
    """Setup the testing namespace"""

    return dict((
        ("TestComponent", TestComponent),
        ("clean_test_components", clean_test_components),
        ("WaitEvent", WaitEvent),
        ("wait_for", wait_for),
        ("call_event", call_event),
        ("PLATFORM", sys.platform),
        ("PYVER", sys.version_info[:3]),
        ("call_event_from_name", call_event_from_name),
    ))

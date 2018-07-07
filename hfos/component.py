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

"""

Configurable Component
======================

Contains
--------

Systemwide configurable component definition. Stores configuration either in
database or as json files.
Enables editing of configuration through frontend.

See also
--------

Provisions


"""
import inspect
import traceback
from sys import exc_info
from uuid import uuid4

from circuits import Component
from circuits.web.controllers import Controller
from copy import deepcopy
from jsonschema import ValidationError
from pymongo.errors import ServerSelectionTimeoutError
from random import randint
from warmongo import model_factory

from hfos.events.system import hfosEvent, authorizedevent, anonymousevent
from hfos.logger import hfoslog, warn, critical, error, verbose
from hfos.schemata.component import ComponentBaseConfigSchema


# from pprint import pprint


def handler(*names, **kwargs):
    """Creates an Event Handler

    This decorator can be applied to methods of classes derived from
    :class:`circuits.core.components.BaseComponent`. It marks the method as a
    handler for the events passed as arguments to the ``@handler`` decorator.
    The events are specified by their name.

    The decorated method's arguments must match the arguments passed to the
    :class:`circuits.core.events.Event` on creation. Optionally, the
    method may have an additional first argument named *event*. If declared,
    the event object that caused the handler to be invoked is assigned to it.

    By default, the handler is invoked by the component's root
    :class:`~.manager.Manager` for events that are propagated on the channel
    determined by the BaseComponent's *channel* attribute.
    This may be overridden by specifying a different channel as a keyword
    parameter of the decorator (``channel=...``).

    Keyword argument ``priority`` influences the order in which handlers
    for a specific event are invoked. The higher the priority, the earlier
    the handler is executed.

    If you want to override a handler defined in a base class of your
    component, you must specify ``override=True``, else your method becomes
    an additional handler for the event.

    **Return value**

    Normally, the results returned by the handlers for an event are simply
    collected in the :class:`circuits.core.events.Event`'s :attr:`value`
    attribute. As a special case, a handler may return a
    :class:`types.GeneratorType`. This signals to the dispatcher that the
    handler isn't ready to deliver a result yet.
    Rather, it has interrupted it's execution with a ``yield None``
    statement, thus preserving its current execution state.

    The dispatcher saves the returned generator object as a task.
    All tasks are reexamined (i.e. their :meth:`next()` method is invoked)
    when the pending events have been executed.

    This feature avoids an unnecessarily complicated chaining of event
    handlers. Imagine a handler A that needs the results from firing an
    event E in order to complete. Then without this feature, the final
    action of A would be to fire event E, and another handler for
    an event ``SuccessE`` would be required to complete handler A's
    operation, now having the result from invoking E available
    (actually it's even a bit more complicated).

    Using this "suspend" feature, the handler simply fires event E and
    then yields ``None`` until e.g. it finds a result in E's :attr:`value`
    attribute. For the simplest scenario, there even is a utility
    method :meth:`circuits.core.manager.Manager.callEvent` that combines
    firing and waiting.
    """

    def wrapper(f):
        if names and isinstance(names[0], bool) and not names[0]:
            f.handler = False
            return f

        if len(names) > 0 and inspect.isclass(names[0]) and \
                issubclass(names[0], hfosEvent):
            f.names = (str(names[0].realname()),)
        else:
            f.names = names

        f.handler = True

        f.priority = kwargs.get("priority", 0)
        f.channel = kwargs.get("channel", None)
        f.override = kwargs.get("override", False)

        args = inspect.getargspec(f)[0]

        if args and args[0] == "self":
            del args[0]
        f.event = getattr(f, "event", bool(args and args[0] == "event"))

        return f

    return wrapper


class LoggingMeta(object):
    """Baseclass for all components that adds naming and logging
    functionality"""

    names = []

    def __init__(self, uniquename=None, *args, **kwargs):
        """Check for configuration issues and instantiate a component"""
        self.uniquename = ""

        if uniquename:
            if uniquename not in self.names:
                self.uniquename = uniquename
                self.names.append(uniquename)
            else:
                hfoslog("Unique component added twice: ", uniquename,
                        lvl=critical, emitter="CORE")
        else:
            while True:
                uniquename = "%s%s" % (self.__class__.__name__,
                                       randint(0, 32768))
                if uniquename not in self.names:
                    self.uniquename = uniquename
                    self.names.append(uniquename)

                    break

    def log(self, *args, **kwargs):
        """Log a statement from this component"""

        func = inspect.currentframe().f_back.f_code
        # Dump the message + the name of this function to the log.

        if 'exc' in kwargs and kwargs['exc'] is True:
            exc_type, exc_obj, exc_tb = exc_info()
            line_no = exc_tb.tb_lineno
            # print('EXCEPTION DATA:', line_no, exc_type, exc_obj, exc_tb)
            args += traceback.extract_tb(exc_tb),
        else:
            line_no = func.co_firstlineno

        sourceloc = "[%.10s@%s:%i]" % (
            func.co_name,
            func.co_filename,
            line_no
        )
        hfoslog(sourceloc=sourceloc, emitter=self.uniquename, *args, **kwargs)


class ConfigurableMeta(LoggingMeta):
    """Meta class to add configuration capabilities to circuits objects"""

    configprops = {}
    configform = []

    def __init__(self, *args, **kwargs):
        """Check for configuration issues and instantiate a component"""

        super(ConfigurableMeta, self).__init__(*args, **kwargs)

        self.configschema = deepcopy(ComponentBaseConfigSchema)

        self.configschema['schema']['properties'].update(self.configprops)
        if len(self.configform) > 0:
            self.configschema['form'] += self.configform
        else:
            self.configschema['form'] = ['*']

        # self.log("[UNIQUECOMPONENT] Config Schema: ", self.configschema,
        #         lvl=critical)
        # pprint(self.configschema)

        # self.configschema['name'] = self.uniquename
        # self.configschema['id'] = "#" + self.uniquename

        # schemastore[self.uniquename] = {'schema': self.configschema,
        # 'form': self.configform}

        self.componentmodel = model_factory(self.configschema['schema'])
        # self.log("Component model: ", lvl=critical)
        # pprint(self.componentmodel._schema)

        self._read_config()
        if not self.config:
            self.log("Creating initial default configuration.")
            try:
                self._set_config()
                self._write_config()
            except ValidationError as e:
                self.log("Error during configuration reading: ", e, type(e),
                         exc=True)

    def register(self, *args):
        """Register a configurable component in the configuration schema
        store"""

        super(ConfigurableMeta, self).register(*args)
        from hfos.database import configschemastore
        # self.log('ADDING SCHEMA:')
        # pprint(self.configschema)
        configschemastore[self.name] = self.configschema

    def unregister(self):
        """Removes the unique name from the systems unique name list"""
        self.names.remove(self.uniquename)
        super(ConfigurableMeta, self).unregister()

    def _read_config(self):
        """Read this component's configuration from the database"""

        try:
            self.config = self.componentmodel.find_one(
                {'name': self.uniquename})
        except ServerSelectionTimeoutError:  # pragma: no cover
            self.log("No database access! Check if mongodb is running "
                     "correctly.", lvl=critical)
        if self.config:
            self.log("Configuration read.", lvl=verbose)
        else:
            self.log("No configuration found.", lvl=warn)
            # self.log(self.config)

    def _write_config(self):
        """Write this component's configuration back to the database"""

        if not self.config:
            self.log("Unable to write non existing configuration", lvl=error)
            return

        self.config.save()
        self.log("Configuration stored.")

    def _set_config(self, config=None):
        """Set this component's initial configuration"""
        if not config:
            config = {}

        try:
            # pprint(self.configschema)
            self.config = self.componentmodel(config)
            # self.log("Config schema:", lvl=critical)
            # pprint(self.config.__dict__)

            # pprint(self.config._fields)

            try:
                name = self.config.name
                self.log("Name set to: ", name, lvl=verbose)
            except (AttributeError, KeyError):  # pragma: no cover
                self.log("Has no name.", lvl=verbose)

            try:
                self.config.name = self.uniquename
            except (AttributeError, KeyError) as e:  # pragma: no cover
                self.log("Cannot set component name for configuration: ", e,
                         type(e), self.name, exc=True, lvl=critical)

            try:
                uuid = self.config.uuid
                self.log("UUID set to: ", uuid, lvl=verbose)
            except (AttributeError, KeyError):
                self.log("Has no UUID", lvl=verbose)
                self.config.uuid = str(uuid4())

            try:
                notes = self.config.notes
                self.log("Notes set to: ", notes, lvl=verbose)
            except (AttributeError, KeyError):
                self.log("Has no notes, trying docstring", lvl=verbose)

                notes = self.__doc__
                if notes is None:
                    notes = "No notes."
                else:
                    notes = notes.lstrip().rstrip()
                    self.log(notes)
                self.config.notes = notes

            try:
                componentclass = self.config.componentclass
                self.log("Componentclass set to: ", componentclass,
                         lvl=verbose)
            except (AttributeError, KeyError):
                self.log("Has no component class", lvl=verbose)
                self.config.componentclass = self.name

        except ValidationError as e:
            self.log("Not setting invalid component configuration: ", e,
                     type(e), exc=True, lvl=error)

            # self.log("Fields:", self.config._fields, lvl=verbose)

    @handler('reload_configuration')
    def reload_configuration(self, event):
        """Event triggered configuration reload"""

        if event.target == self.uniquename:
            self.log('Reloading configuration')
            self._read_config()


class LoggingComponent(LoggingMeta, Component):
    """Logging capable component for simple HFOS components"""

    def __init__(self, uniquename=None, *args, **kwargs):
        LoggingMeta.__init__(self, uniquename)
        Component.__init__(self, *args, **kwargs)


class ConfigurableController(ConfigurableMeta, Controller):
    """Configurable controller for direct web access"""

    def __init__(self, uniquename=None, *args, **kwargs):
        ConfigurableMeta.__init__(self, uniquename)
        Controller.__init__(self, *args, **kwargs)


class ConfigurableComponent(ConfigurableMeta, Component):
    """Configurable component for default HFOS modules"""

    def __init__(self, uniquename=None, *args, **kwargs):
        ConfigurableMeta.__init__(self, uniquename)
        Component.__init__(self, *args, **kwargs)


class ExampleComponent(ConfigurableComponent):
    """Exemplary component to demonstrate basic component usage"""

    configprops = {
        'setting': {'type': 'string', 'title': 'Some Setting',
                    'description': 'Some string setting.', 'default': 'Yay'},
    }

    def __init__(self, *args, **kwargs):
        """Show how the component initialization works and test this by
        adding a log statement."""
        super(ExampleComponent, self).__init__("EXAMPLE", *args, **kwargs)

        self.log("Example component started")
        # self.log(self.config)

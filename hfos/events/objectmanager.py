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


Module: Events
==============

Major HFOS event declarations


"""

from circuits.core import Event

from hfos.logger import hfoslog, events
# from hfos.ui.clientobjects import User
from hfos.events.system import authorizedevent


# Object Management

class objectevent(Event):
    """A unspecified objectevent"""

    def __init__(self, uuid, schema, client, *args, **kwargs):
        super(objectevent, self).__init__(*args, **kwargs)

        self.uuid = uuid
        self.schema = schema
        self.client = client

        hfoslog("Object event created: ", self.__doc__,
                self.__dict__, lvl=events, emitter="OBJECT-EVENT")


class objectchange(objectevent):
    """A stored object has been successfully modified"""


class objectcreation(objectevent):
    """A new object has been successfully created"""


class objectdeletion(objectevent):
    """A stored object has been successfully deleted"""


# Backend-side object change

class updatesubscriptions(Event):
    """A backend component needs to write changes to an object.
    Clients that are subscribed should be notified etc.
    """

    def __init__(self, schema, data, *args, **kwargs):
        super(updatesubscriptions, self).__init__(*args, **kwargs)

        self.schema = schema
        self.data = data

        hfoslog("Object event created: ", self.__doc__,
                self.__dict__, lvl=events, emitter="OBJECT-EVENT")


class search(authorizedevent):
    """A client requires a schema to validate data or display a form"""


class getlist(authorizedevent):
    """A client requires a schema to validate data or display a form"""


class get(authorizedevent):
    """A client requires a schema to validate data or display a form"""


class put(authorizedevent):
    """A client requires a schema to validate data or display a form"""


class change(authorizedevent):
    """A client requires a schema to validate data or display a form"""


class delete(authorizedevent):
    """A client requires a schema to validate data or display a form"""


class subscribe(authorizedevent):
    """A client requires a schema to validate data or display a form"""


class unsubscribe(authorizedevent):
    """A client requires a schema to validate data or display a form"""

class remove_role(authorizedevent):
    pass

class add_role(authorizedevent):
    pass
"""


Module: Events
==============

Major HFOS event declarations

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from circuits.core import Event

from hfos.logger import hfoslog, critical, events
from hfos.ui.clientobjects import User
from hfos.events.system import authorizedevent

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


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

class updatesubscriptions(objectevent):
    """A backend component needs to write changes to an object.
    Clients that are subscribed should be notified etc.
    """

    def __init__(self, data, *args, **kwargs):
        super(updatesubscriptions, self).__init__(*args, **kwargs)

        self.data = data


class search(authorizedevent):
    """A client requires a schema to validate data or display a form"""


class list(authorizedevent):
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

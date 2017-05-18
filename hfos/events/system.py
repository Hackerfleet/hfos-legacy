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

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

AuthorizedEvents = {}


def get_user_events():
    global AuthorizedEvents
    return AuthorizedEvents


def populate_user_events():
    global AuthorizedEvents

    def inheritors(klass):
        subclasses = {}
        subclasses_set = set()
        work = [klass]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses_set:
                    # pprint(child.__dict__)
                    name = child.__module__ + "." + child.__name__
                    if name.startswith('hfos'):

                        subclasses_set.add(child)
                        event = {
                            'event': child,
                            'name': name,
                            'doc': child.__doc__,
                            'args': []
                        }

                        if child.__module__ in subclasses:
                            subclasses[child.__module__][
                                child.__name__] = event
                        else:
                            subclasses[child.__module__] = {
                                child.__name__: event
                            }
                    work.append(child)
        return subclasses

    AuthorizedEvents = inheritors(authorizedevent)


class authorizedevent(Event):
    """Base class for events for logged in users."""

    def __getattr__(self, name):
        """For circuits handler decorator to enable module/event namespaces"""
        if name == 'name':
            return self.__module__ + '.' + self.__class__.__name__
        else:
            super(authorizedevent, self).__getattr__(name)

    def __init__(self, user, action, data, client, *args):
        """
        Sets up an authorized event.

        :param user: User object from :py:class:hfos.web.clientmanager.User
        :param action:
        :param data:
        :param client:
        :param args:
        :return:
        """

        assert isinstance(user, User)

        self.name = self.__module__ + '.' + self.__class__.__name__
        super(authorizedevent, self).__init__(*args)
        self.user = user
        self.action = action
        self.data = data
        self.client = client

    @classmethod
    def realname(cls):
        # For circuits manager to enable module/event namespaces
        return cls.__module__ + '.' + cls.__name__


# Authenticator Events

class profilerequest(authorizedevent):
    """A user has changed his profile"""

    def __init__(self, *args):
        """

        :param user: Userobject of client
        :param data: The new profile data
        """
        super(profilerequest, self).__init__(*args)

        hfoslog("Profile update request: ", self.__dict__,
                lvl=events, emitter="PROFILE-EVENT")


# Frontend assembly events

class frontendbuildrequest(Event):
    def __init__(self, force=False, install=False, *args):
        super(frontendbuildrequest, self).__init__(*args)
        self.force = force
        self.install = install


class componentupdaterequest(frontendbuildrequest):
    pass


# Debugger

class logtailrequest(authorizedevent):
    pass


class debugrequest(authorizedevent):
    """Debugging event"""

    def __init__(self, *args):
        super(debugrequest, self).__init__(*args)

        hfoslog('CREATED.', lvl=critical, emitter="DEBUG-EVENT")

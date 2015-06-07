"""
Hackerfleet Operating System - Backend

Module: Auth
============

Authentication (and later Authorization) system

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from circuits import Component, handler

from database import userobject, profileobject
from events import authentication
from hfos.logger import hfoslog, error, warn, critical

from uuid import uuid4


class Authenticator(Component):
    """
    Authenticates users against the database.
    """

    channel = "hfosweb"

    @handler("authenticationrequest", channel="auth")
    def authenticationrequest(self, event):
        """Handles authentication requests from clients"""
        hfoslog("Auth: Auth request for ", event.username)

        useraccount = None

        try:
            useraccount = userobject.find_one({'username': event.username})
            hfoslog("Auth: Account: %s" % useraccount._fields)
        except Exception as e:
            hfoslog("Auth: No userobject due to error: ", e, type(e))

        if useraccount:
            hfoslog("Auth: User found!")

            if useraccount.passhash == event.passhash:
                hfoslog("Auth: Hash matches, fetching profile.")

                try:
                    userprofile = profileobject.find_one({'uuid': str(useraccount.uuid)})
                    hfoslog("Auth: Profile: ", userprofile, useraccount.uuid)
                    useraccount.passhash = ""
                    self.fireEvent(
                        authentication(useraccount.username, (useraccount, userprofile), event.clientuuid,
                                       useraccount.uuid,
                                       event.sock),
                        "auth")
                except Exception as e:
                    hfoslog("Auth: No profile due to error: ", e, type(e), lvl=error)
            else:
                hfoslog("Auth: Password wrong!", lvl=warn)

        else:
            # TODO: Write registration function
            hfoslog("Auth: Creating user")
            try:
                newuser = userobject({'username': event.username, 'passhash': event.passhash, 'uuid': str(uuid4())})
                newuser.save()
                newprofile = profileobject({'uuid': str(newuser.uuid)})
                newprofile.components.enabled = ["dasboard", "map", "weather", "settings"]
                newprofile.save()
                self.fireEvent()
            except Exception as e:
                hfoslog("Auth: Problem creating new user: ", type(e), e)

    def profilerequest(self, event):
        """Handles client profile actions"""

        hfoslog("Auth: Profile update %s" % event)

        if event.action != "update":
            hfoslog("Auth: Unsupported profile action: ", event, lvl=warn)
            return

        try:
            newprofile = event.data
            hfoslog("Auth: Updating with %s " % newprofile)

            userprofile = profileobject.find_one({'uuid': event.user.useruuid})

            if event.user.useruuid != newprofile['uuid']:
                hfoslog("Auth: User tried to manipulate wrong profile.", lvl=warn)
                return

            if not userprofile:
                hfoslog("Auth: No profile! Creating a new one..", lvl=critical)
                userprofile = profileobject()

            hfoslog("Auth: Updating %s" % userprofile)

            userprofile.update(newprofile)
            userprofile.save()

            hfoslog("Profile stored.")
            # TODO: Give client feedback
        except Exception as e:
            hfoslog("Exception! %s %s" % (type(e), e), lvl=error)

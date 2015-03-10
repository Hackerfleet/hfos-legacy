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

from .database import userobject, profileobject
from .events import authentication
from hfos.logger import hfoslog, error, warn


class Authenticator(Component):
    """
    Authenticates users against the database.
    """

    channel = "auth"

    @handler("authenticationrequest")
    def authenticationrequest(self, event):
        """Handles authentication requests from clients"""
        hfoslog("Auth request for ", event.username)

        useraccount = None

        try:
            useraccount = userobject.find_one({'username': event.username})
            hfoslog("Account: %s" % useraccount)
        except Exception as e:
            hfoslog("No userobject due to error: ", e, type(e))

        if useraccount:
            hfoslog("User found!")

            if useraccount.passhash == event.passhash:
                hfoslog("Hash matches, fetching profile.")

                try:
                    userprofile = profileobject.find_one({'uuid': useraccount.uuid})
                    #del(useraccount['_id'], useraccount['passhash'])
                    self.fireEvent(
                        authentication(event.username, (useraccount, userprofile), event.uuid, useraccount.uuid,
                                       event.sock),
                        "wsserver")
                except Exception as e:
                    hfoslog("No profile due to error: ", e, type(e), lvl=error)
            else:
                hfoslog("Password wrong!", lvl=warn)

        else:
            # TODO: Write registration function
            hfoslog("Creating user")
            try:
                # New user gets registered with the first uuid he happens to turn up
                newuser = userobject({'username': event.username, 'passhash': event.passhash, 'uuid': str(event.uuid)})
                newuser.save()
                newprofile = profileobject({'uuid': str(newuser.uuid)})
                newprofile.save()
            except Exception as e:
                hfoslog("Problem creating new user: ", type(e), e)

    @handler("profileupdate")
    def profileupdate(self, event):
        """Handles client profile updates"""

        hfoslog("Profileupdate %s" % event)

        try:
            newprofile = event.profile
            hfoslog("Got: %s " % newprofile)
            userprofile = profileobject.find_one({'uuid': newprofile['uuid']})
            if not userprofile:
                hfoslog("No profile, whoa?! Creating a new one..", lvl=error)
                userprofile = profileobject()
            hfoslog("Have: %s" % userprofile)
            userprofile.update(event.profile)
            userprofile.save()
            hfoslog("Profile stored.")
            # TODO: Give client feedback
        except Exception as e:
            hfoslog("Exception! %s %s" % (type(e), e))

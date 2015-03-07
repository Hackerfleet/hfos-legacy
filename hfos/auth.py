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


class Authenticator(Component):
    """
    Authenticates users against the database.
    """

    channel = "auth"

    @handler("authenticationrequest")
    def authenticationrequest(self, event):
        """Handles authentication requests from clients"""
        print("AUTHENTICATE: Request %s" % event)
        print("Username: %s, Passhash: %s" % (event.username, event.passhash))
        try:
            #useraccount = self._authcollection.find_one({'username': event.username})
            useraccount = userobject.find_one({'username': event.username})
            print("AUTHENTICATE: Account: %s" % useraccount)
            if useraccount:
                print("AUTHENTICATE: User found!")
                print(useraccount.__dict__)
                if useraccount.passhash == event.passhash:
                    print("AUTHENTICATE: Hash matches, fetching profile.")
                    userprofile = profileobject.find_one({'uuid': useraccount.uuid})
                    #del(useraccount['_id'], useraccount['passhash'])
                    self.fireEvent(authentication(event.username, (useraccount, userprofile), event.uuid, event.sock),
                                   "wsserver")

            else:
                # TODO: Write registration function
                print("AUTHENTICATE: Creating user")

                # New user gets registered with the first uuid he happens to turn up
                newuser = userobject({'username': event.username, 'passhash': event.passhash, 'uuid': str(event.uuid)})
                newuser.save()
                newprofile = profileobject({'uuid': str(newuser.uuid)})
                newprofile.save()

        except Exception as e:
            print("AUTHENTICATE: Exception! %s %s" % (type(e), e))

    @handler("profileupdate")
    def profileupdate(self, event):
        """Handles client profile updates"""

        print("AUTHENTICATE: Profileupdate %s" % event)

        try:
            newprofile = event.profile
            print("AUTHENTICATE: Got: %s " % newprofile)
            userprofile = profileobject.find_one({'uuid': newprofile['uuid']})
            print("AUTHENTICATE: Have: %s" % userprofile)
            userprofile.update(event.profile)
            userprofile.save()
        except Exception as e:
            print("AUTHENTICATE: Exception! %s %s" % (type(e), e))

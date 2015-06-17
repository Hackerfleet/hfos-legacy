"""

Module: Auth
============

Authentication (and later Authorization) system

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from uuid import uuid4

from circuits import Component, handler

from hfos.database import userobject, profileobject
from hfos.events import authentication
from hfos.logger import hfoslog, error, warn, debug, verbose


class Authenticator(Component):
    """
    Authenticates users against the database.
    """

    channel = "hfosweb"

    @handler("authenticationrequest", channel="auth")
    def authenticationrequest(self, event):
        """Handles authentication requests from clients
        :param event: AuthenticationRequest with user's credentials
        """

        hfoslog("[AUTH] Auth request for ", event.username)

        useraccount = None

        try:
            useraccount = userobject.find_one({'username': event.username})
            hfoslog("[AUTH] Account: %s" % useraccount._fields, lvl=debug)
        except Exception as e:
            hfoslog("[AUTH] No userobject due to error: ", e, type(e), lvl=error)

        if useraccount:
            hfoslog("[AUTH] User found.")

            if useraccount.passhash == event.passhash:
                hfoslog("[AUTH] Passhash matches, fetching profile.", lvl=debug)

                try:
                    userprofile = profileobject.find_one({'uuid': str(useraccount.uuid)})
                    hfoslog("[AUTH] Profile: ", userprofile, useraccount.uuid)
                    useraccount.passhash = ""
                    self.fireEvent(
                        authentication(useraccount.username, (useraccount, userprofile), event.clientuuid,
                                       useraccount.uuid,
                                       event.sock),
                        "auth")
                except Exception as e:
                    hfoslog("[AUTH] No profile due to error: ", e, type(e), lvl=error)
            else:
                hfoslog("[AUTH] Password was wrong!", lvl=warn)

        else:
            hfoslog("[AUTH] Creating user")
            try:
                newuser = userobject({'username': event.username, 'passhash': event.passhash, 'uuid': str(uuid4())})
                newuser.save()
            except Exception as e:
                hfoslog("[AUTH] Problem creating new user: ", type(e), e, lvl=error)
                return
            try:
                newprofile = profileobject({'uuid': str(newuser.uuid)})
                hfoslog("[AUTH] New profile uuid: ", newprofile.uuid, lvl=verbose)

                newprofile.components = {'enabled': ["dasboard", "map", "weather", "settings"]}
                newprofile.save()
            except Exception as e:
                hfoslog("[AUTH] Problem creating new profile: ", type(e), e, lvl=error)
                return

            try:
                self.fireEvent(authentication(newuser.username, (newuser, newprofile), event.clientuuid,
                                              newuser.uuid,
                                              event.sock),
                               "auth")
            except Exception as e:
                hfoslog("[AUTH] Error during new account confirmation transmission", e, lvl=error)

    def profilerequest(self, event):
        """Handles client profile actions
        :param event:
        """

        hfoslog("[AUTH] Profile update %s" % event)

        if event.action != "update":
            hfoslog("[AUTH] Unsupported profile action: ", event, lvl=warn)
            return

        try:
            newprofile = event.data
            hfoslog("[AUTH] Updating with %s " % newprofile, lvl=debug)

            userprofile = profileobject.find_one({'uuid': event.user.useruuid})

            if event.user.useruuid != userprofile.uuid:
                hfoslog("[AUTH] User tried to manipulate wrong profile.", lvl=warn)
                return

            hfoslog("[AUTH] Updating %s" % userprofile, lvl=debug)

            userprofile.update(newprofile)
            userprofile.save()

            hfoslog("[AUTH] Profile stored.")
            # TODO: Give client feedback
        except Exception as e:
            hfoslog("[AUTH] General profile request error %s %s" % (type(e), e), lvl=error)

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

from hfos.database import userobject, profileobject, clientconfigobject
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

        hfoslog("[AUTH] Auth request for ", event.username, event.clientuuid)

        useraccount = None
        clientconfig = None
        userprofile = None

        try:
            useraccount = userobject.find_one({'username': event.username})
            hfoslog("[AUTH] Account: %s" % useraccount._fields, lvl=debug)
        except Exception as e:
            hfoslog("[AUTH] No userobject due to error: ", e, type(e), lvl=error)

        if useraccount:
            hfoslog("[AUTH] User found.")

            if useraccount.passhash == event.passhash:
                hfoslog("[AUTH] Passhash matches, checking client and profile.", lvl=debug)

                if event.requestedclientuuid != event.clientuuid:
                    # Client requests to get an existing client configuration

                    clientconfig = clientconfigobject.find_one({'clientuuid': event.requestedclientuuid})

                    if clientconfig:
                        hfoslog("[AUTH] Checking client configuration permissions", lvl=debug)
                        if clientconfig.useruuid != useraccount.uuid:
                            clientconfig = None
                            hfoslog("[AUTH] Unauthorized client configuration requested", lvl=warn)
                    else:
                        hfoslog("[AUTH] Unknown client configuration requested: ", event.requestedclientuuid, lvl=warn)

                if not clientconfig:
                    hfoslog("[AUTH] Creating new default client configuration")
                    # Either no configuration was found or requested
                    # -> Create a new client configuration

                    clientconfig = clientconfigobject()
                    clientconfig.clientuuid = event.clientuuid
                    clientconfig.name = "New client"
                    clientconfig.description = "New client configuration"
                    clientconfig.useruuid = useraccount.uuid
                    # TODO: Make sure the profile is only saved if the client could store it, too
                    clientconfig.save()

                try:
                    userprofile = profileobject.find_one({'uuid': str(useraccount.uuid)})
                    hfoslog("[AUTH] Profile: ", userprofile, useraccount.uuid, lvl=debug)

                    useraccount.passhash = ""
                    self.fireEvent(
                        authentication(useraccount.username, (useraccount, userprofile, clientconfig), event.clientuuid,
                                       useraccount.uuid,
                                       event.sock),
                        "auth")
                except Exception as e:
                    hfoslog("[AUTH] No profile due to error: ", e, type(e), lvl=error)
            else:
                hfoslog("[AUTH] Password was wrong!", lvl=warn)

            hfoslog("[AUTH] Done with Login request", lvl=debug)

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
                # TODO: Clone or reference systemwide default configuration
                newclientconfig = clientconfigobject()
                newclientconfig.clientuuid = event.clientuuid
                newclientconfig.name = "New client"
                newclientconfig.description = "New client configuration"
                newclientconfig.useruuid = useraccount.uuid
                newclientconfig.save()
            except Exception as e:
                hfoslog("[AUTH] Problem creating new clientconfig: ", type(e), e, lvl=error)
                return

            try:
                self.fireEvent(
                    authentication(newuser.username, (newuser, newprofile, newclientconfig), event.clientuuid,
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

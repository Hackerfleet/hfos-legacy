"""


Module: Events
==============

Major HFOS event declarations

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from circuits.core import Event
from hfos.logger import hfoslog, debug, critical, verbose, warn, events
from hfos.web.clientobjects import User

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


class AuthorizedEvent(Event):
    """Base class for events for logged in users."""

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

        super(AuthorizedEvent, self).__init__(*args)
        self.user = user
        self.action = action
        self.data = data
        self.client = client


# Debugger


class debugrequest(AuthorizedEvent):
    """Debugging event"""

    def __init__(self, *args):
        super(debugrequest, self).__init__(*args)

        hfoslog('[DEBUG-EVENT] CREATED.', lvl=critical)


# Clientmanager Events


class send(Event):
    """Send a packet to a known client by UUID"""

    def __init__(self, uuid, packet, sendtype="client",
                 raw=False, username=None, *args):
        """

        :param uuid: Unique User ID of known connection
        :param packet: Data packet to transmit to client
        :param args: Further Args
        """
        super(send, self).__init__(*args)

        if uuid is None and username is None:
            hfoslog("[SEND-EVENT] No recipient (uuid/name) given!", lvl=warn)
        self.uuid = uuid
        self.packet = packet
        self.username = username
        self.sendtype = sendtype
        self.raw = raw

        hfoslog("[CM-EVENT] Send event generated:", uuid, packet, sendtype,
                lvl=events)


class broadcast(Event):
    """Send a packet to a known client by UUID"""

    def __init__(self, broadcasttype, content, *args):
        """

        :param uuid: Unique User ID of known connection
        :param packet: Data packet to transmit to client
        :param args: Further Args
        """
        super(broadcast, self).__init__(*args)
        self.broadcasttype = broadcasttype
        self.content = content

        hfoslog("[CM-EVENT] Broadcast event generated:", broadcasttype,
                content, lvl=events)


class clientdisconnect(Event):
    """
    A client has disconnected from the system. This has to propagate to all
    subscription based and other user aware components.

    :param clientuuid: UUID of disconnecting client
    :param useruuid: UUID of disconnecting user
    :param args:

    """

    def __init__(self, clientuuid, useruuid=None, *args):
        super(clientdisconnect, self).__init__(*args)
        self.clientuuid = clientuuid
        self.useruuid = useruuid

        hfoslog("[CM-EVENT] Client disconnect event generated:", clientuuid,
                useruuid, lvl=events)


class userlogin(Event):
    """
    A user has logged in to the system. This has to propagate to all
    subscription based and other user aware components.

    :param clientuuid: UUID of disconnecting client
    :param useruuid: UUID of disconnecting user
    :param args:

    """

    def __init__(self, clientuuid, useruuid, *args):
        super(userlogin, self).__init__(*args)
        self.clientuuid = clientuuid
        self.useruuid = useruuid

        hfoslog("[CM-EVENT] User login event generated:", clientuuid, useruuid,
                lvl=events)


# Authenticator Events


class authenticationrequest(Event):
    """A client wants to authenticated a connection"""

    def __init__(self, username, passhash, clientuuid, requestedclientuuid,
                 sock, auto, *args):
        """

        :param username: Account username
        :param passhash: Account md5 hash
        :param clientuuid: Unique User ID of known connection
        :param sock: Associated Socket
        :param args: Further Args
        """
        super(authenticationrequest, self).__init__(*args)

        self.username = username
        self.passhash = passhash
        self.sock = sock
        self.clientuuid = clientuuid
        self.requestedclientuuid = requestedclientuuid
        self.auto = auto


class authentication(Event):
    """Authentication has been granted to a client"""

    def __init__(self, username, userdata, clientuuid, useruuid, sock, *args):
        """

        :param username: Account username
        :param userdata: Tuple containing both useraccount and userprofile
        :param uuid: Unique User ID of known connection
        :param sock: Associated Socket
        :param args: Further Args
        """
        super(authentication, self).__init__(*args)

        self.username = username
        self.userdata = userdata
        self.clientuuid = clientuuid
        self.useruuid = useruuid
        self.sock = sock

        hfoslog("[AUTH-EVENT] Authentication granted:", self.__dict__,
                lvl=events)


class profilerequest(AuthorizedEvent):
    """A user has changed his profile"""

    def __init__(self, *args):
        """

        :param user: Userobject of client
        :param data: The new profile data
        """
        super(profilerequest, self).__init__(*args)

        hfoslog("[PROFILE-EVENT] Profile update request: ", self.__dict__,
                lvl=events)


# Schemata requests


class schemarequest(AuthorizedEvent):
    """A client requires a schema to validate data or display a form"""


# Object Manager requests


class objectmanagerrequest(AuthorizedEvent):
    """A client requires a schema to validate data or display a form"""


class objectevent(Event):
    """A unspecified objectevent"""

    def __init__(self, uuid, schema, *args, **kwargs):
        super(objectevent, self).__init__(*args, **kwargs)

        self.uuid = uuid
        self.schema = schema

        hfoslog("[OBJECT-EVENT] Object event created: ", self.__doc__,
                self.__dict__, lvl=events)


# Backend-side object change

class updatesubscriptions(objectevent):
    """A backend component needs to write changes to an object.
    Clients that are subscribed should be notified etc.
    """

    def __init__(self, data, *args, **kwargs):
        super(updatesubscriptions, self).__init__(*args, **kwargs)

        self.data = data


# Object change

class objectchange(objectevent):
    """A stored object has been successfully modified"""


class objectcreation(objectevent):
    """A new object has been successfully created"""


class objectdeletion(objectevent):
    """A stored object has been successfully deleted"""


# Chat requests


class chatrequest(AuthorizedEvent):
    """A new chat event has been generated by the client"""


# Wiki requests


class wikirequest(AuthorizedEvent):
    """A new wiki event has been generated by the client"""


# Camera requests


class camerarequest(AuthorizedEvent):
    """A new camera event has been generated by the client"""


# Mapview Events


class mapviewrequest(AuthorizedEvent):
    """A mapview request for an update or subscription management"""

    def __init__(self, *args):
        super(mapviewrequest, self).__init__(*args)

        hfoslog("[MVS-EVENT] Request generated", lvl=events)


# Mapview Events


class alertrequest(AuthorizedEvent):
    """A client related alert event"""

    def __init__(self, *args):
        super(alertrequest, self).__init__(*args)

        hfoslog("[ALERT-EVENT] Request generated", lvl=events)


class mapviewbroadcast(Event):
    """A user changed his mapview and subscribers need to get notified"""

    def __init__(self, sender, mapview, *args):
        """

        :param sender: Originating User object
        :param mapview: New mapview update
        :param args: Further Args
        """
        super(mapviewbroadcast, self).__init__(*args)
        self.sender = sender
        self.mapview = mapview

        hfoslog("[MVS-EVENT] Broadcast-Event generated", lvl=events)


# Layer Events


class layermanagementrequest(Event):
    """A mapview request for an update or subscription management"""

    def __init__(self, sender, request, *args):
        """

        :param sender: Originating Client Object
        :param requesttype: One of "Update", "Subscribe", "Unsubscribe"
        :param mapview: The new mapview object
        :param args: Further Args
        """
        super(layermanagementrequest, self).__init__(*args)
        self.sender = sender
        self.request = request

        hfoslog("[LM-EVENT] Request generated", lvl=events)


class layerrequest(AuthorizedEvent):
    """A geojson-layer data request"""

    def __init__(self, *args):
        super(layerrequest, self).__init__(*args)

        hfoslog("[LM-EVENT] Request generated", lvl=events)


# Sensor Events


class sensordata(Event):
    """New sensordata has been parsed"""

    def __init__(self, data, timestamp, bus):
        """

        :param data: Parsed NMEA? Data
        """
        super(sensordata, self).__init__()
        self.data = data
        self.timestamp = timestamp
        self.bus = bus


# Navigation Data Events

class referenceframe(Event):
    """New sensordata has been parsed"""

    def __init__(self, data):
        """

        :param data: Parsed NMEA? Data
        """
        super(referenceframe, self).__init__()
        self.data = data
        hfoslog("[NAVDATA-EVENT] Reference frame generated: ", data,
                lvl=events)


# Remote Control requests

class remotecontrolrequest(AuthorizedEvent):
    """A client wants to remote control a servo"""


# Remote Control events

class remotecontrolupdate(Event):
    """A client wants to remote control a servo"""

    def __init__(self, controldata, *args):
        super(remotecontrolupdate, self).__init__(*args)
        self.controldata = controldata


class libraryrequest(AuthorizedEvent):
    pass


class frontendbuildrequest(Event):
    def __init__(self, force=False, install=False, *args):
        super(frontendbuildrequest, self).__init__(*args)
        self.force = force
        self.install = install


class componentupdaterequest(frontendbuildrequest):
    pass


class logtailrequest(AuthorizedEvent):
    pass


AuthorizedEvents = {
    'alert': alertrequest,
    'camera': camerarequest,
    'chat': chatrequest,
    'debugger': debugrequest,
    'layer': layerrequest,
    'library': libraryrequest,
    'mapview': mapviewrequest,
    'objectmanager': objectmanagerrequest,
    'profile': profilerequest,
    'remotectrl': remotecontrolrequest,
    'schema': schemarequest,
    'wiki': wikirequest
}

from circuits import Event
from hfos.logger import hfoslog, warn, events

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


class authenticationrequest(Event):
    """A client wants to authenticated a connection"""

    def __init__(self, username, password, clientuuid, requestedclientuuid,
                 sock, auto, *args):
        """

        :param username: Account username
        :param password: Account md5 hash
        :param clientuuid: Unique User ID of known connection
        :param sock: Associated Socket
        :param args: Further Args
        """
        super(authenticationrequest, self).__init__(*args)

        self.username = username
        self.password = password
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

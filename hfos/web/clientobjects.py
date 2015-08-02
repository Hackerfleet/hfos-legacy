__author__ = 'riot'


class Socket(object):
    """
    Socket metadata object
    """

    def __init__(self, ip, clientuuid):
        """

        :param ip: Associated Internet protocol address
        :param clientuuid: Unique Uniform ID of this client
        """
        super(Socket, self).__init__()
        self.ip = ip
        self.clientuuid = clientuuid


class Client(object):
    """
    Client metadata object
    """

    def __init__(self, sock, ip, clientuuid, useruuid=None, name='', config=None):
        """

        :param sock: Associated connection
        :param ip: Associated Internet protocol address
        :param clientuuid: Unique Uniform ID of this client
        """
        super(Client, self).__init__()

        self.sock = sock
        self.ip = ip
        self.uuid = clientuuid
        self.useruuid = useruuid
        if name == '':
            self.name = clientuuid
        else:
            self.name = name
        self.config = config


class User(object):
    """
    Authenticated clients with profile etc
    """

    def __init__(self, account, profile, uuid):
        """

        :param account: userobject
        :param profile: profileobject
        :param uuid: profileobject
        :param clients: List of clients' UUIDs
        :param args:
        """
        super(User, self).__init__()
        self.clients = []
        self.uuid = uuid
        self.profile = profile
        self.account = account

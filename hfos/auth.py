from circuits import Component, handler, Event

from pymongo import MongoClient


class authrequest(Event):

    def __init__(self, username, passhash, uuid, sock, *args):
        super(authrequest, self).__init__(*args)

        self.username = username
        self.passhash = passhash
        self.sock = sock
        self.uuid = uuid

class authgranted(Event):

    def __init__(self, username, useraccount, uuid, sock, *args):
        super(authgranted, self).__init__(*args)

        self.username = username
        self.useraccount = useraccount
        self.uuid = uuid
        self.sock = sock
        print(self.__dict__)


class Auth(Component):

    channel="wsserver"

    def __init__(self, host="127.0.0.1", port=27017, *args):
        """

        :param host:
        :param port:
        :param user:
        :param password:
        """

        super(Auth, self).__init__(*args)

        self._host = host
        self._port = port
        self._client = MongoClient(host=self._host, port=self._port)
        self._authcollection = self._client['hfos']['auth']

    @handler("authrequest")
    def authrequest(self, event):
        print("AUTH: Request %s" % (event))
        print("Username: %s, Passhash: %s" % (event.username, event.passhash))
        try:
            useraccount = self._authcollection.find_one({'username': event.username})
            if useraccount:
                print("AUTH: User found!")
                print(useraccount)
                if useraccount['passhash'] == event.passhash:
                    print("AUTH: Hash matches!")
                    del(useraccount['_id'], useraccount['passhash'])
                    self.fireEvent(authgranted(event.username, useraccount, event.uuid, event.sock))

            else:
                # TODO: Write registration function
                print("AUTH: User created - HACK")
                self._authcollection.insert({'username': event.username, 'passhash': event.passhash})
        except Exception as e:
            print("AUTH: Exception! %s %s" % (type(e), e))

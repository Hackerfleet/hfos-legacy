from json import dumps

import click
from circuits import handler, Manager, Component, Debugger
from circuits.net.events import write
from circuits.web.websockets.client import WebSocketClient

from dev.tools import ask

from pprint import pprint


class HFOSClient(Component):
    def __init__(self, *args, **kwargs):
        super(HFOSClient, self).__init__(*args, **kwargs)
        self.url = '{protocol}://{host}:{port}/websocket'.format(**kwargs)
        self.client = WebSocketClient(self.url).register(self)
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')

        self.messages = []

    @handler("registered", channel='ws')
    def connected(self, *args):
        print('Transmitting login')
        packet = {
            'component': 'auth',
            'action': 'login',
            'data': {
                'username': self.username,
                'password': self.password
            }
        }

        self.fireEvent(write(dumps(packet)), 'ws')

    @handler("read", channel='ws')
    def read(self, *args):
        msg = args[0]
        self.messages.append(msg)
        print(len(self.messages), '>>>', msg)


@click.command()
@click.option("--protocol", help="Define protocol for server (ws/wss)",
              type=str, default='wss')
@click.option("--port", help="Define port for server", type=int,
              default=443)
@click.option("--host", help="Define hostname for server", type=str,
              default='0.0.0.0')
@click.option("-u", "--username", help="Specify username", type=str,
              default='anonymous')
@click.option("-p", "--password", help="Specify password", type=str,
              default='')
@click.option("--debug", help="Start debugger", type=bool,
              default=False)
def main(**kwargs):
    user = kwargs.get('username')
    if user != 'anonymous' and kwargs.get('password') == '':
        kwargs['password'] = ask('Enter password for ' + user + ':',
                                 password=True)

    manager = Manager()
    if kwargs.get('debug'):
        debugger = Debugger().register(manager)
    client = HFOSClient(**kwargs).register(manager)

    manager.run()


if __name__ == '__main__':
    main()

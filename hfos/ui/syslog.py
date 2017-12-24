# coding=utf-8
from circuits import Event, Timer

from hfos.component import ConfigurableComponent, handler
from hfos.events.client import send # , clientdisconnect
from hfos.events.system import authorizedevent
from hfos.logger import error, debug


class history(authorizedevent):
    pass


class subscribe(authorizedevent):
    pass


class Syslog(ConfigurableComponent):
    """
    System log access component

    Handles all the frontend log history requests.

    """

    configprops = {
        'log_file': {
            'type': 'string',
            'default': '/var/log/hfos.log',
            'title': 'Filename',
            'description': 'File path of logfile (usually /var/log/hfos.log)'
        }
    }

    def __init__(self, *args):
        super(Syslog, self).__init__('SYSLOG', *args)

        self.log("Started.")

        self.subscribers = []

        self.log_file = open(self.config.log_file)
        self.log_position = 0

        self.follow_timer = Timer(1, Event.create('syslog_follow'),
                                  persist=True)

    @handler(subscribe)
    def subscribe(self, event):
        self.subscribers.append(event.client.uuid)

    @handler('clientdisconnect', priority=1000)
    def disconnect(self, event):
        self.log('Disconnected: ', event.clientuuid, lvl=debug)
        if event.clientuuid in self.subscribers:
            self.subscribers.remove(event.clientuuid)

    def _logupdate(self, new_messages):
        packet = {
            'component': 'hfos.ui.syslog',
            'action': 'update',
            'data': new_messages
        }

        for subscriber in self.subscribers:
            self.fireEvent(send(subscriber, packet, fail_quiet=True))

    @handler('syslog_follow')
    def follow(self):
        where = self.log_file.tell()
        line = self.log_file.readline()
        if not line:
            self.log_file.seek(where)
        else:
            self._logupdate(line)

    @handler(history)
    def history(self, event):
        try:
            limit = event.data['limit']
            end = event.data['end']
        except (KeyError, AttributeError) as e:
            self.log('Error during event lookup:', e, type(e), exc=True,
                     lvl=error)
            return

        self.log('History requested:', limit, end, lvl=debug)

        messages = []

        history_packet = {
            'component': 'hfos.ui.syslog',
            'action': 'history',
            'data': {
                'limit': limit,
                'end': end,
                'history': messages
            }
        }
        self.fireEvent(send(event.client.uuid, history_packet))

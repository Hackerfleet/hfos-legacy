from hfos.component import ConfigurableComponent, handler
from hfos.database import objectmodels
from hfos.events.client import send, clientdisconnect
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

    def __init__(self, *args):
        super(Syslog, self).__init__('SYSLOG', *args)

        self.log("Started.")

        self.subscribers = []

    @handler(subscribe)
    def subscribe(self, event):
        self.subscribers.append(event.client.uuid)

    @handler(clientdisconnect)
    def disconnect(self, event):
        if event.clientuuid in self.subscribers:
            self.subscribers.remove(event.clientuuid)

    @handler("logupdate", channel='logger')
    def logupdate(self, event):
        self.log('Updating syslog viewers', lvl=debug)
        packet = {
            'component': 'hfos.ui.syslog',
            'action': 'update',
            'data': event.message.serializablefields()
        }

        for subscriber in self.subscribers:
            self.fireEvent(send(subscriber, packet))

    @handler(history)
    def history(self, event):
        try:
            limit = event.data['limit']
            end = event.data['end']
        except (KeyError, AttributeError) as e:
            self.log('Error during event lookup:', e, type(e), exc=True,
                     lvl=error)
            return

        self.log('History requested:', limit, end)

        messages = []

        om = objectmodels['logmessage']
        try:
            for msg in om.find(
                    {
                        'timestamp': {'$lte': end}
                    },
                    sort=[('timestamp', -1)],
                    limit=limit
            ):
                messages.insert(0, msg.serializablefields())
        except Exception as e:
            self.log('Error during history lookup:', e, type(e), exc=True,
                     lvl=error)
            return

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


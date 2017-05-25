"""

Module: Configurator
=====================

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.events.client import send
from hfos.component import ConfigurableComponent, authorizedevent, handler
from hfos.schemata.component import ComponentConfigSchemaTemplate as Schema
from hfos.database import configschemastore, ValidationError, objectmodels
from hfos.logger import error, warn, verbose, hilight
from warmongo import model_factory

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

from pprint import pprint


class list(authorizedevent):
    """A client requires a schema to validate data or display a form"""


class get(authorizedevent):
    """A client requires a schema to validate data or display a form"""


class put(authorizedevent):
    """A client requires a schema to validate data or display a form"""


class Configurator(ConfigurableComponent):
    """
    Handles schemata requests from clients.
    """

    channel = "hfosweb"

    configprops = {}

    def __init__(self, *args):
        super(Configurator, self).__init__('CONF', *args)

    def _check_permission(self, event):
        user = objectmodels['user'].find_one({'uuid': event.user.uuid})

        if 'admin' not in user.roles:
            self.log('Missing permission to configure components',
                     lvl=warn)

            return False
        return True

    @handler(list)
    def list(self, event):
        """Processes configuration list requests

        :param event: ConfigRequest with actions
        * Get
        * Store
        * Restart?
        """

        try:

            componentlist = model_factory(Schema).find({})
            data = []
            for comp in componentlist:
                data.append({
                    'name': comp.name,
                    'uuid': comp.uuid,
                    'class': comp.componentclass,
                    'active': comp.active
                })

            data = sorted(data, key=lambda x: x['name'])

            response = {
                'component': 'hfos.ui.configurator',
                'action': 'list',
                'data': data
            }
            self.fireEvent(send(event.client.uuid, response))
            return
        except Exception as e:
            self.log("List error: ", e, type(e), lvl=error, exc=True)

    @handler(put)
    def put(self, event):
        self.log("Configuration put request ",
                 event.user)

        try:
            if self._check_permission(event) is False:
                raise PermissionError

            component = model_factory(Schema).find_one({
                'uuid': event.data['uuid']
            })

            component.update(event.data)
            component.save()

            response = {
                'component': 'hfos.ui.configurator',
                'action': 'put',
                'data': True
            }
            self.log('Updated component configuration:',
                     component.name)
        except (KeyError, ValueError, ValidationError, PermissionError) as e:
            response = {
                'component': 'hfos.ui.configurator',
                'action': 'put',
                'data': False
            }
            self.log('Storing component configuration failed: ',
                     type(e), e, exc=True, lvl=error)

        self.fireEvent(send(event.client.uuid, response))
        return

    @handler(get)
    def get(self, event):
        try:
            comp = event.data['uuid']
        except KeyError:
            comp = None

        if not comp:
            self.log('Invalid get request without schema or component',
                     lvl=error)
            return

        self.log("Config data get  request for ", event.data, "from",
                 event.user)

        component = model_factory(Schema).find_one({
            'uuid': comp
        })
        response = {
            'component': 'hfos.ui.configurator',
            'action': 'get',
            'data': component.serializablefields()
        }
        self.fireEvent(send(event.client.uuid, response))

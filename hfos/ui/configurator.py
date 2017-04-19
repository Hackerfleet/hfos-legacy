"""

Module: Configurator
=====================

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.events.client import send
from hfos.component import ConfigurableComponent
from hfos.schemata.component import ComponentConfigSchemaTemplate as Schema
from hfos.database import configschemastore, ValidationError, objectmodels
from hfos.logger import error, warn, verbose, hilight
from warmongo import model_factory

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

from pprint import pprint


class Configurator(ConfigurableComponent):
    """
    Handles schemata requests from clients.
    """

    channel = "hfosweb"

    configprops = {}

    def __init__(self, *args):
        super(Configurator, self).__init__('CONF', *args)

    def configrequest(self, event):
        """Handles configuration requests.

        :param event: ConfigRequest with actions
        * Get
        * Store
        * Restart?
        """

        try:
            user = objectmodels['user'].find_one({'uuid': event.user.uuid})

            if 'admin' not in user.roles:
                self.log('Missing permission to configure components',
                         lvl=warn)
                response = {'component': 'configurator',
                            'action': 'Error',
                            'data': 'Perm'
                            }
                self.fireEvent(send(event.client.uuid, response))
                return

            if event.action == "List":
                self.log("Component list request from",
                         event.user, lvl=verbose)

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

                response = {'component': 'configurator',
                            'action': 'List',
                            'data': data
                            }
                self.fireEvent(send(event.client.uuid, response))
                return

            elif event.action == "Put":
                self.log("Configuration put request ",
                         event.user)

                try:
                    component = model_factory(Schema).find_one({
                        'uuid': event.data['uuid']
                    })

                    component.update(event.data)
                    component.save()

                    response = {
                        'component': 'configurator',
                        'action': 'Put',
                        'data': True
                    }
                    self.log('Updated component configuration:',
                             component.name)
                except (KeyError, ValueError, ValidationError) as e:
                    response = {'component': 'configurator',
                                'action': 'Put',
                                'data': False
                                }
                    self.log('Storing component configuration failed: ',
                             type(e), e, exc=True, lvl=error)

                self.fireEvent(send(event.client.uuid, response))
                return

            try:
                comp = event.data['uuid']
            except KeyError:
                comp = None

            if not comp:
                self.log('Invalid request without schema or component',
                         lvl=error)
                return

            if event.action == "Get":
                self.log("Config data request for ", event.data, "from",
                         event.user)

                component = model_factory(Schema).find_one({
                    'uuid': comp
                })
                response = {'component': 'configurator',
                            'action': 'Get',
                            'data': component.serializablefields()
                            }
                self.fireEvent(send(event.client.uuid, response))

        except Exception as e:
            self.log("Overall error: ", e, type(e), lvl=error, exc=True)

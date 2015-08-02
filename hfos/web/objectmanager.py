"""

Module: OM
============

OM manager

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from uuid import uuid4

from circuits import Component

from hfos.logger import hfoslog, debug, error, warn, critical
from hfos.events import send

from hfos.database import objectmodels, ValidationError

WARNSIZE = 500


class ObjectManager(Component):
    """
    Object Manager

    Handles
    * incoming object requests and updates
    """

    channel = "hfosweb"

    def __init__(self, *args):
        super(ObjectManager, self).__init__(*args)

        hfoslog("[OM] Started")

    def objectmanagerrequest(self, event):
        """OM event handler for incoming events
        :param event: OMRequest with incoming OM pagename and pagedata
        """

        hfoslog("[OM] Event: '%s'" % event.__dict__)
        try:
            action = event.action
            data = event.data
            schema = data['schema']

            result = None

            if action == "list":
                if schema in objectmodels.keys():
                    if 'filter' in data:
                        filter = data['filter']
                    else:
                        filter = {}

                    if 'fields' in data:
                        fields = data['fields']
                    else:
                        fields = []

                    objlist = []

                    if objectmodels[schema].count(filter) > WARNSIZE:
                        hfoslog("[OM] Getting a very long list of items for ", schema, lvl=warn)

                    for item in objectmodels[schema].find(filter):
                        try:
                            listitem = {'uuid': item.uuid, 'name': item.name}
                            for field in fields:
                                if field in item._fields:
                                    listitem[field] = item._fields[field]
                                else:
                                    listitem[field] = None

                            objlist.append(listitem)
                        except Exception as e:
                            hfoslog("[OM] Faulty object or field: ", item._fields, fields, lvl=error)
                    hfoslog("[OM] Generated object list: ", objlist)

                    result = {'component': 'objectmanager',
                              'action': 'list',
                              'data': {'schema': schema,
                                       'list': objlist
                                       }
                              }
                else:
                    hfoslog("[OM] List for unavailable schema requested: ", schema, lvl=warn)

            elif action == "get":
                uuid = data['uuid']
                obj = None

                if schema in objectmodels.keys():
                    obj = objectmodels[schema].find_one({'uuid': uuid})

                if not obj:
                    hfoslog("[OM] Object not found: ", data)
                    obj = objectmodels[schema]({'uuid': str(uuid4())})
                else:
                    hfoslog("[OM] Object found, delivering: ", data)

                result = {'component': 'objectmanager',
                          'action': 'get',
                          'data': obj.serializablefields()
                          }

            elif action == "put":
                try:
                    putobj = data['obj']
                    uuid = putobj['uuid']
                except KeyError:
                    hfoslog("[OM] Put request with missing arguments!", event, lvl=critical)
                    return

                try:
                    obj = objectmodels[schema].find_one({'uuid': uuid})
                    if obj:

                        hfoslog("[OM] Updating object:", obj._fields, lvl=debug)
                        obj.update(putobj)

                    else:
                        obj = objectmodels[schema](putobj)
                        hfoslog("[OM] Storing object:", obj._fields, lvl=debug)
                        try:
                            obj.validate()
                        except ValidationError:
                            hfoslog("[OM] Validation of new object failed!", data, lvl=warn)

                    obj.save()

                    hfoslog("[OM] Object stored.")

                    result = {'component': 'objectmanager',
                              'action': 'put',
                              'data': (True, obj.uuid),
                              }
                except Exception as e:
                    hfoslog("[OM] Error during object storage:", e, type(e), lvl=error)

            else:
                hfoslog("[OM] Unsupported action: ", action, event, event.__dict__, lvl=warn)
                return

            if result:
                try:
                    self.fireEvent(send(event.client.uuid, result))
                except Exception as e:
                    hfoslog("[OM] Transmission error before broadcast: %s" % e, lvl=error)

        except Exception as e:
            hfoslog("[OM] Error: '%s' %s" % (e, type(e)), lvl=error)

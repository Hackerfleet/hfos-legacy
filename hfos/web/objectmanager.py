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
from hfos.events import send, objectcreation, objectchange, objectdeletion
from hfos.database import objectmodels, collections, ValidationError
from hfos.schemata import schemastore
import pymongo

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

        self.subscriptions = {}

        hfoslog("[OM] Started")

    def objectmanagerrequest(self, event):
        """OM event handler for incoming events
        :param event: OMRequest with incoming OM pagename and pagedata
        """

        hfoslog("[OM] Event: '%s'" % event.__dict__)
        try:
            action = event.action
            data = event.data
            if 'schema' in data:
                schema = data['schema']

            result = None
            notification = None

            if action == "list":
                if schema in objectmodels.keys():
                    if 'filter' in data:
                        objectfilter = data['filter']
                    else:
                        objectfilter = {}

                    if 'fields' in data:
                        fields = data['fields']
                    else:
                        fields = []

                    objlist = []

                    if objectmodels[schema].count(objectfilter) > WARNSIZE:
                        hfoslog("[OM] Getting a very long list of items for ", schema, lvl=warn)

                    for item in objectmodels[schema].find(objectfilter):
                        try:
                            listitem = {'uuid': item.uuid}
                            if 'name' in item._fields:
                                listitem['name'] = item.name

                            for field in fields:
                                if field in item._fields:
                                    listitem[field] = item._fields[field]
                                else:
                                    listitem[field] = None

                            objlist.append(listitem)
                        except Exception as e:
                            hfoslog("[OM] Faulty object or field: ", e, type(e), item._fields, fields, lvl=error)
                    hfoslog("[OM] Generated object list: ", objlist)

                    result = {'component': 'objectmanager',
                              'action': 'list',
                              'data': {'schema': schema,
                                       'list': objlist
                                       }
                              }
                else:
                    hfoslog("[OM] List for unavailable schema requested: ", schema, lvl=warn)

            elif action == "search":
                if schema in objectmodels.keys():
                    if 'filter' in data:
                        objectfilter = data['filter']
                    else:
                        objectfilter = {}

                    # objectfilter['$text'] = {'$search': str(data['search'])}
                    objectfilter = {'name': {'$regex': str(data['search']), '$options': '$i'}}

                    # if 'fields' in data:
                    #    fields = data['fields']
                    # else:
                    fields = []

                    reqid = data['req']

                    objlist = []

                    if collections[schema].count() > WARNSIZE:
                        hfoslog("[OM] Getting a very long list of items for ", schema, lvl=warn)

                    hfoslog('[OM] Objectfilter: ', objectfilter, ' Schema: ', schema, lvl=warn)
                    # for item in collections[schema].find(objectfilter):
                    for item in collections[schema].find(objectfilter):
                        hfoslog("[OM] Search found item: ", item, lvl=warn)
                        try:
                            # TODO: Fix bug in warmongo that needs this workaround:
                            item = objectmodels[schema](item)
                            listitem = {'uuid': item.uuid}
                            if 'name' in item._fields:
                                listitem['name'] = item.name

                            for field in fields:
                                if field in item._fields:
                                    listitem[field] = item._fields[field]
                                else:
                                    listitem[field] = None

                            objlist.append(listitem)
                        except Exception as e:
                            hfoslog("[OM] Faulty object or field: ", e, type(e), item._fields, fields, lvl=error)
                    hfoslog("[OM] Generated object search list: ", objlist)

                    result = {'component': 'objectmanager',
                              'action': 'search',
                              'data': {'schema': schema,
                                       'list': objlist,
                                       'req': reqid
                                       }
                              }
                else:
                    hfoslog("[OM] List for unavailable schema requested: ", schema, lvl=warn)

            elif action == "get":
                uuid = data['uuid']

                storageobject = None

                if schema in objectmodels.keys() and uuid.upper != "CREATE":
                    storageobject = objectmodels[schema].find_one({'uuid': uuid})

                if not storageobject:
                    hfoslog("[OM] Object not found, creating: ", data)

                    storageobject = objectmodels[schema]({'uuid': str(uuid4())})

                    if "useruuid" in schemastore[schema]['schema']['properties']:
                        storageobject.useruuid = event.user.uuid
                        hfoslog("[OM] Attached initial owner's id: ", event.user.uuid)
                else:
                    hfoslog("[OM] Object found, delivering: ", data)

                result = {'component': 'objectmanager',
                          'action': 'get',
                          'data': storageobject.serializablefields()
                          }

            elif action == "subscribe":
                uuid = data

                if uuid in self.subscriptions:
                    self.subscriptions[uuid].append(event.client.uuid)
                else:
                    self.subscriptions[uuid] = [event.client.uuid]

                result = {'component': 'objectmanager',
                          'action': 'subscribe',
                          'data': {'uuid': uuid, 'success': True}
                          }

            elif action == "unsubscribe":
                # TODO: Automatic Unsubscription
                uuid = data

                if uuid in self.subscriptions:
                    self.subscriptions[uuid].remove(event.client.uuid)

                    if len(self.subscriptions[uuid]) == 0:
                        del (self.subscriptions[uuid])

                result = {'component': 'objectmanager',
                          'action': 'unsubscribe',
                          'data': {'uuid': uuid, 'success': True}
                          }

            elif action == "put":
                try:
                    clientobject = data['obj']
                    uuid = clientobject['uuid']
                except KeyError:
                    hfoslog("[OM] Put request with missing arguments!", event, lvl=critical)
                    return

                try:
                    if uuid != 'create':
                        storageobject = objectmodels[schema].find_one({'uuid': uuid})
                    else:
                        clientobject['uuid'] = str(uuid4())
                        storageobject = objectmodels[schema](clientobject)

                    if storageobject:
                        hfoslog("[OM] Updating object:", storageobject._fields, lvl=debug)
                        storageobject.update(clientobject)

                    else:
                        storageobject = objectmodels[schema](clientobject)
                        hfoslog("[OM] Storing object:", storageobject._fields, lvl=debug)
                        try:
                            storageobject.validate()
                        except ValidationError:
                            hfoslog("[OM] Validation of new object failed!", clientobject, lvl=warn)
                            return

                    storageobject.save()

                    hfoslog("[OM] Object stored.")

                    # Notify backend listeners

                    if uuid == 'create':
                        notification = objectcreation(storageobject.uuid, schema)
                    else:
                        notification = objectchange(storageobject.uuid, schema)

                    # Notify frontend subscribers

                    if uuid in self.subscriptions:
                        update = {'component': 'objectmanager',
                                  'action': 'update',
                                  'data': storageobject.serializablefields()
                                  }

                        for recipient in self.subscriptions[uuid]:
                            self.fireEvent(send(recipient, update))

                    result = {'component': 'objectmanager',
                              'action': 'put',
                              'data': (True, storageobject.uuid),
                              }
                except Exception as e:
                    hfoslog("[OM] Error during object storage:", e, type(e), data, lvl=error)

            elif action == 'delete':
                try:
                    uuid = data['uuid']

                    if schema in objectmodels.keys():
                        hfoslog("[OM] Looking for object to be deleted.", lvl=debug)
                        storageobject = objectmodels[schema].find_one({'uuid': uuid})
                        hfoslog("[OM] Found object.", lvl=debug)

                        hfoslog("[OM] Fields:", storageobject._fields, "\n\n\n", storageobject.__dict__)
                        storageobject.delete()

                        hfoslog("[OM] Preparing notification.", lvl=debug)
                        notification = objectdeletion(uuid, schema)

                        if uuid in self.subscriptions:
                            deletion = {'component': 'objectmanager',
                                        'action': 'deletion',
                                        'data': uuid
                                        }
                            for recipient in self.subscriptions[uuid]:
                                self.fireEvent(send(recipient, deletion))

                            del (self.subscriptions[uuid])

                        result = {'component': 'objectmanager',
                                  'action': 'delete',
                                  'data': (True, storageobject.uuid),
                                  }
                except Exception as e:
                    hfoslog("[OM] Error during delete request: ", e, type(e), lvl=error)

            else:
                hfoslog("[OM] Unsupported action: ", action, event, event.__dict__, lvl=warn)
                return

            if notification:
                try:
                    self.fireEvent(notification)
                except Exception as e:
                    hfoslog("[OM] Transmission error during notification: %s" % e, lvl=error)

            if result:
                try:
                    self.fireEvent(send(event.client.uuid, result))
                except Exception as e:
                    hfoslog("[OM] Transmission error during response: %s" % e, lvl=error)

        except Exception as e:
            print()
            hfoslog("[OM] Overall Error: '%s' %s" % (e, type(e)), exc=True)

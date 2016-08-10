"""

Module: OM
==========

OM manager

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from uuid import uuid4

from hfos.events.system import objectcreation, objectchange, objectdeletion
from hfos.events.client import send
from hfos.component import ConfigurableComponent
from hfos.database import objectmodels, collections, ValidationError, schemastore
from hfos.logger import debug, error, warn, critical

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

WARNSIZE = 500


class ObjectManager(ConfigurableComponent):
    """
    Handles object requests and updates.
    """

    channel = "hfosweb"

    configprops = {}

    def __init__(self, *args):
        super(ObjectManager, self).__init__('OM', *args)

        self.subscriptions = {}

        self.log("Started")

    def objectmanagerrequest(self, event):
        """OM event handler for incoming events
        :param event: OMRequest with incoming OM pagename and pagedata
        """

        self.log("Event: '%s'" % event.__dict__)
        action = event.action
        data = event.data
        if action not in ['subscribe', 'unsubscribe']:
            if 'schema' in data:
                schema = data['schema']
            else:
                self.log("No Schema given, cannot act!", lvl=critical)
                return

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
                    self.log("Getting a very long list of items for ", schema,
                             lvl=warn)

                for item in objectmodels[schema].find(objectfilter):
                    try:
                        if fields in ('*', ['*']):
                            objlist.append(item.serializablefields())
                        else:
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
                        self.log("Faulty object or field: ", e, type(e),
                                 item._fields, fields, lvl=error,
                                 exc=True)
                self.log("Generated object list: ", objlist)

                result = {'component': 'objectmanager',
                          'action': 'list',
                          'data': {'schema': schema,
                                   'list': objlist
                                   }
                          }
            else:
                self.log("Schemata: ", objectmodels.keys())
                self.log("List for unavailable schema requested: ", schema,
                         lvl=warn)

        elif action == "search":
            if schema in objectmodels.keys():
                if 'filter' in data:
                    objectfilter = data['filter']
                else:
                    objectfilter = {}

                # objectfilter['$text'] = {'$search': str(data['search'])}
                objectfilter = {
                    'name': {'$regex': str(data['search']), '$options': '$i'}}

                # if 'fields' in data:
                #    fields = data['fields']
                # else:
                fields = []

                reqid = data['req']

                objlist = []

                if collections[schema].count() > WARNSIZE:
                    self.log("Getting a very long list of items for ", schema,
                             lvl=warn)

                self.log("Objectfilter: ", objectfilter, ' Schema: ', schema,
                         lvl=warn)
                # for item in collections[schema].find(objectfilter):
                for item in collections[schema].find(objectfilter):
                    self.log("Search found item: ", item, lvl=warn)
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
                        self.log("Faulty object or field: ", e, type(e),
                                 item._fields, fields, lvl=error)
                self.log("Generated object search list: ", objlist)

                result = {'component': 'objectmanager',
                          'action': 'search',
                          'data': {'schema': schema,
                                   'list': objlist,
                                   'req': reqid
                                   }
                          }
            else:
                self.log("List for unavailable schema requested: ", schema,
                         lvl=warn)

        elif action == "get":
            try:
                uuid = data['uuid']
            except KeyError:
                self.log('Object with no uuid requested:', schema, data,
                         lvl=error)
                return

            if 'subscribe' in data:
                subscribe = data['subscribe']
            else:
                subscribe = False

            storageobject = None

            if schema in objectmodels.keys() and uuid.upper != "CREATE":
                storageobject = objectmodels[schema].find_one({'uuid': uuid})

            if not storageobject:
                self.log("Object not found, creating: ", data)

                storageobject = objectmodels[schema]({'uuid': str(uuid4())})

                if "useruuid" in schemastore[schema]['schema']['properties']:
                    storageobject.useruuid = event.user.uuid
                    self.log("Attached initial owner's id: ", event.user.uuid)
            else:
                self.log("Object found, delivering: ", data)

            if subscribe:
                if uuid in self.subscriptions:
                    if not event.client.uuid in self.subscriptions[uuid]:
                        self.subscriptions[uuid].append(event.client.uuid)
                else:
                    self.subscriptions[uuid] = [event.client.uuid]

            result = {'component': 'objectmanager',
                      'action': 'get',
                      'data': storageobject.serializablefields()
                      }

        elif action == "subscribe":
            uuid = data

            if uuid in self.subscriptions:
                if not event.client.uuid in self.subscriptions[uuid]:
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
            result, notification = self._put(schema, data)

        elif action == 'delete':
            result, notification = self._delete(schema, data)

        elif action == 'change':
            result, notification = self._change(schema, data)

        else:
            self.log("Unsupported action: ", action, event, event.__dict__,
                     lvl=warn)
            return

        if notification:
            try:
                self.fireEvent(notification)
            except Exception as e:
                self.log("Transmission error during notification: %s" % e,
                         lvl=error)

        if result:
            try:
                self.fireEvent(send(event.client.uuid, result))
            except Exception as e:
                self.log("Transmission error during response: %s" % e,
                         lvl=error)

    def updatesubscriptions(self, event):
        """OM event handler for to be stored and client shared objectmodels
        :param event: OMRequest with uuid, schema and object data
        """

        self.log("Event: '%s'" % event.__dict__)
        try:
            data = event.data
            self._updateSubscribers(data)

        except Exception as e:
            self.log("Error during subscription update: ", type(e), e,
                     exc=True)

    def _change(self, schema, data):
        try:
            uuid = data['uuid']

            change = data['change']
            field = change['field']
            newdata = change['value']

        except KeyError as e:
            self.log("Update request with missing arguments!", data, e,
                     lvl=critical)

        storageobject = None

        try:
            storageobject = objectmodels[schema].find_one({'uuid': uuid})
        except Exception as e:
            self.log('Change for unknown object requested:', schema,
                     data, lvl=warn)

        if storageobject is not None:
            self.log("Changing object:", storageobject._fields, lvl=debug)
            storageobject._fields[field] = newdata

            self.log("Storing object:", storageobject._fields, lvl=debug)
            try:
                storageobject.validate()
            except ValidationError:
                self.log("Validation of changed object failed!",
                         storageobject, lvl=warn)

            storageobject.save()

            self.log("Object stored.")
            return True, None
        else:
            self.log("Object update failed. No object.", lvl=warn)
            return False, None

    def _put(self, schema, data):
        try:
            clientobject = data['obj']
            uuid = clientobject['uuid']
        except KeyError:
            self.log("Put request with missing arguments!", data, lvl=critical)

        try:
            if uuid != 'create':
                storageobject = objectmodels[schema].find_one({'uuid': uuid})
            else:
                clientobject['uuid'] = str(uuid4())
                storageobject = objectmodels[schema](clientobject)

            if storageobject:
                self.log("Updating object:", storageobject._fields, lvl=debug)
                storageobject.update(clientobject)

            else:
                storageobject = objectmodels[schema](clientobject)
                self.log("Storing object:", storageobject._fields, lvl=debug)
                try:
                    storageobject.validate()
                except ValidationError:
                    self.log("Validation of new object failed!", clientobject,
                             lvl=warn)

            storageobject.save()

            self.log("Object stored.")

            # Notify backend listeners

            if uuid == 'create':
                notification = objectcreation(storageobject.uuid, schema)
            else:
                notification = objectchange(storageobject.uuid, schema)

            self._updateSubscribers(storageobject)

            result = {'component': 'objectmanager',
                      'action': 'put',
                      'data': (True, storageobject.uuid),
                      }

            return result, notification

        except Exception as e:
            self.log("Error during object storage:", e, type(e), data,
                     lvl=error, exc=True)

    def _updateSubscribers(self, updateobject):
        # Notify frontend subscribers

        if updateobject.uuid in self.subscriptions:
            update = {'component': 'objectmanager',
                      'action': 'update',
                      'data': updateobject.serializablefields()
                      }

            for recipient in self.subscriptions[updateobject.uuid]:
                self.fireEvent(send(recipient, update))

    def _delete(self, schema, data):
        if True:  # try:
            uuid = data['uuid']

            if schema in objectmodels.keys():
                self.log("Looking for object to be deleted.", lvl=debug)
                storageobject = objectmodels[schema].find_one({'uuid': uuid})
                self.log("Found object.", lvl=debug)

                self.log("Fields:", storageobject._fields, "\n\n\n",
                         storageobject.__dict__)
                storageobject.delete()

                self.log("Preparing notification.", lvl=debug)
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
                return result, notification
            else:
                self.log("Unknown schema encountered: ", schema, lvl=warn)
                # except Exception as e:
                #    self.log("Error during delete request: ", e, type(e),
                # lvl=error)

"""

Module: OM
==========

OM manager

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from uuid import uuid4

from hfos.events.objectmanager import objectcreation, objectchange, \
    objectdeletion, list, search, get, change, put, delete, subscribe, \
    unsubscribe
from hfos.events.client import send
from hfos.component import handler, ConfigurableComponent
from hfos.database import objectmodels, collections, ValidationError, \
    schemastore
from hfos.logger import verbose, debug, error, warn, critical, hilight

from pprint import pprint

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

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

    def _check_permissions(self, subject, action, obj):
        self.log('Roles of user:', subject.account.roles, lvl=debug)

        if 'owner' in obj.perms[action]:
            try:
                if subject.uuid == obj.owner:
                    self.log('Access granted via ownership', lvl=verbose)
                    return True
            except AttributeError as e:
                self.log('Schema has ownership permission but no owner:',
                         obj._schema['name'], obj._fields, e, type(e),
                         lvl=warn, exc=True)
        for role in subject.account.roles:
            if role in obj.perms[action]:
                self.log('Access granted', lvl=verbose)
                return True

        self.log('Access denied', lvl=verbose)
        return False

    def _cancel_by_permission(self, schema, data, client):
        self.log('No permission:', schema, data, client.account.name,
                 lvl=error)

        msg = {
            'component': 'hfos.events.objectmanager',
            'action': 'Fail',
            'data': (False, 'No permission.', data)
        }
        self.fire(send(client.uuid, msg))

    def _cancel_by_error(self, event):
        self.log('Malformed request!', lvl=error)

        msg = {
            'component': 'hfos.events.objectmanager',
            'action': 'Fail',
            'data': 'MALFORMED'
        }
        self.fire(send(event.client.uuid, msg))

    def _get_schema(self, event):
        try:
            data = event.data
        except AttributeError:
            return

        if 'schema' not in data or data['schema'] not in \
                objectmodels.keys():
            thing = data['schema'] if 'schema' in data else None
            self.log("List for unavailable schema requested: ",
                     thing,
                     lvl=warn)
            result = {
                'component': 'objectmanager',
                'action': "noschema",
                'data': thing
            }
            self.fireEvent(send(event.client.uuid, result))
            return
        else:
            schema = data['schema']

        return schema

    def _get_filter(self, event):
        data = event.data
        if 'filter' in data:
            object_filter = data['filter']
        else:
            object_filter = {}

        return object_filter

    def _get_args(self, event):
        try:
            data = event.data
            schema = self._get_schema(event)
            user = event.user
            client = event.client

            return data, schema, user, client
        except AttributeError:
            self.log('Malformed request: ', exc=True, lvl=warn)
            return

    def _respond(self, notification, result, event):
        if notification:
            try:
                self.log('Firing notification', lvl=verbose)
                self.fireEvent(notification)
            except Exception as e:
                self.log("Transmission error during notification: %s" % e,
                         lvl=error)

        if result:
            try:
                self.log('Transmitting result', lvl=verbose)
                self.fireEvent(send(event.client.uuid, result))
            except Exception as e:
                self.log("Transmission error during response: %s" % e,
                         lvl=error)

    @handler(get)
    def get(self, event):
        data, schema, user, client = self._get_args(event)

        object_filter = self._get_filter(event)

        if 'subscribe' in data:
            do_subscribe = data['subscribe'] is True
        else:
            do_subscribe = False

        try:
            uuid = str(data['uuid'])
        except (KeyError, TypeError):
            uuid = ""

        opts = schemastore[schema].get('options', {})
        hidden = opts.get('hidden', [])

        if object_filter == {}:
            if uuid == "":
                self.log('Object with no filter/uuid requested:', schema,
                         data,
                         lvl=warn)
                return
            object_filter = {'uuid': uuid}

        storage_object = None
        storage_object = objectmodels[schema].find_one(object_filter)

        if not storage_object:
            if uuid.upper == "CREATE":
                # TODO: Fix this, a request for an existing object is a
                # request for an existing object, a creation request is
                # not.

                self.log("Object not found, creating: ", data)

                storage_object = objectmodels[schema](
                    {'uuid': str(uuid4())})

                if "owner" in schemastore[schema]['schema']['properties']:
                    storage_object.owner = event.user.uuid
                    self.log("Attached initial owner's id: ", event.user.uuid)
            else:
                self.log("Object not found and not willing to create.",
                         lvl=warn)
                result = {
                    'component': 'hfos.events.objectmanager',
                    'action': 'noobject',
                    'data': {
                        'schema': schema,
                    }
                }

        if storage_object:
            self.log(storage_object.perms, lvl=debug)
            self.log("Object found, checking permissions: ", data, lvl=debug)

            if not self._check_permissions(user, 'read',
                                           storage_object):
                self._cancel_by_permission(schema, data, event.client)
                return

            for field in hidden:
                storage_object._fields.pop(field, None)

            if do_subscribe and uuid != "":
                self.log('Updating subscriptions', lvl=debug)
                if uuid in self.subscriptions:
                    if event.client.uuid not in self.subscriptions[uuid]:
                        self.subscriptions[uuid].append(event.client.uuid)
                else:
                    self.subscriptions[uuid] = [event.client.uuid]

            result = {
                'component': 'hfos.events.objectmanager',
                'action': 'get',
                'data': storage_object.serializablefields()
            }

        self._respond(None, result, event)

    @handler(search)
    def search(self, event):
        data, schema, user, client = self._get_args(event)

        # object_filter['$text'] = {'$search': str(data['search'])}
        if 'fulltext' in data:
            object_filter = {
                'name': {
                    '$regex': str(data['search']),
                    '$options': '$i'
                }
            }
        else:
            if isinstance(data['search'], dict):
                object_filter = data['search']
            else:
                object_filter = {}

        if 'fields' in data:
            fields = data['fields']
        else:
            fields = []

        request_id = data['req']

        object_list = []

        if collections[schema].count() > WARNSIZE:
            self.log("Getting a very long list of items for ", schema,
                     lvl=warn)

        opts = schemastore[schema].get('options', {})
        hidden = opts.get('hidden', [])

        self.log("object_filter: ", object_filter, ' Schema: ', schema,
                 "Fields: ", fields,
                 lvl=verbose)
        # for item in collections[schema].find(object_filter):
        for item in collections[schema].find(object_filter):
            self.log("Search found item: ", item, lvl=verbose)
            try:
                # TODO: Fix bug in warmongo that needs this workaround:
                item = objectmodels[schema](item)
                list_item = {'uuid': item.uuid}
                if fields in ('*', ['*']):
                    item_fields = item.serializablefields()
                    for field in hidden:
                        item_fields.pop(field, None)
                    object_list.append(item_fields)
                else:
                    if 'name' in item._fields:
                        list_item['name'] = item.name

                    for field in fields:
                        if field in item._fields and field not in \
                                hidden:
                            list_item[field] = item._fields[field]
                        else:
                            list_item[field] = None

                    object_list.append(list_item)
            except Exception as e:
                self.log("Faulty object or field: ", e, type(e),
                         item._fields, fields, lvl=error)
        # self.log("Generated object search list: ", object_list)

        result = {
            'component': 'hfos.events.objectmanager',
            'action': 'search',
            'data': {
                'schema': schema,
                'list': object_list,
                'req': request_id
            }
        }

        self._respond(None, result, event)

    @handler(list)
    def objectlist(self, event):
        data, schema, user, client = self._get_args(event)
        object_filter = self._get_filter(event)
        self.log('Object list for', schema, 'requested from',
                 user.account.name, lvl=debug)

        if 'fields' in data:
            fields = data['fields']
        else:
            fields = []

        object_list = []

        opts = schemastore[schema].get('options', {})
        hidden = opts.get('hidden', [])

        if objectmodels[schema].count(object_filter) > WARNSIZE:
            self.log("Getting a very long list of items for ", schema,
                     lvl=warn)

        for item in objectmodels[schema].find(object_filter):
            try:
                if fields in ('*', ['*']):
                    item_fields = item.serializablefields()
                    for field in hidden:
                        item_fields.pop(field, None)
                    object_list.append(item_fields)
                else:
                    list_item = {'uuid': item.uuid}

                    if 'name' in item._fields:
                        list_item['name'] = item._fields['name']

                    for field in fields:
                        if field in item._fields and field not in hidden:
                            list_item[field] = item._fields[field]
                        else:
                            list_item[field] = None

                    object_list.append(list_item)
            except Exception as e:
                self.log("Faulty object or field: ", e, type(e),
                         item._fields, fields, lvl=error, exc=True)
        # self.log("Generated object list: ", object_list)

        result = {
            'component': 'hfos.events.objectmanager',
            'action': 'list',
            'data': {
                'schema': schema,
                'list': object_list
            }
        }

        self._respond(None, result, event)

    @handler(change)
    def change(self, event):
        data, schema, user, client = self._get_args(event)

        try:
            uuid = data['uuid']
            change = data['change']
            field = change['field']
            new_data = change['value']

        except KeyError as e:
            self.log("Update request with missing arguments!", data, e,
                     lvl=critical)
            return

        storage_object = None

        try:
            storage_object = objectmodels[schema].find_one({'uuid': uuid})
        except Exception as e:
            self.log('Change for unknown object requested:', schema,
                     data, lvl=warn)

        if storage_object is not None:
            if not self._check_permissions(user, 'write', storage_object):
                self._cancel_by_permission(schema, data, client)
                return

            self.log("Changing object:", storage_object._fields, lvl=debug)
            storage_object._fields[field] = new_data

            self.log("Storing object:", storage_object._fields, lvl=debug)
            try:
                storage_object.validate()
            except ValidationError:
                self.log("Validation of changed object failed!",
                         storage_object, lvl=warn)

            storage_object.save()

            self.log("Object stored.")
            self._respond(None, True, event)
        else:
            self.log("Object update failed. No object.", lvl=warn)
            self._respond(None, False, event)

    @handler(put)
    def put(self, event):
        data, schema, user, client = self._get_args(event)

        try:
            clientobject = data['obj']
            uuid = clientobject['uuid']
        except KeyError:
            self.log("Put request with missing arguments!", data, lvl=critical)
            return

        try:
            if uuid != 'create':
                storage_object = objectmodels[schema].find_one({'uuid': uuid})
            else:
                clientobject['uuid'] = str(uuid4())
                clientobject['owner'] = user.uuid
                storage_object = objectmodels[schema](clientobject)

            if storage_object:
                self.log("Updating object:", storage_object._fields, lvl=debug)
                storage_object.update(clientobject)

            else:
                storage_object = objectmodels[schema](clientobject)
                self.log("Storing object:", storage_object._fields, lvl=debug)
                try:
                    storage_object.validate()
                except ValidationError:
                    self.log("Validation of new object failed!", clientobject,
                             lvl=warn)

            storage_object.save()

            self.log("Object stored.")

            # Notify backend listeners

            if uuid == 'create':
                notification = objectcreation(storage_object.uuid, schema,
                                              client)
            else:
                notification = objectchange(storage_object.uuid, schema, client)

            self._update_subscribers(storage_object)

            result = {
                'component': 'hfos.events.objectmanager',
                'action': 'put',
                'data': (True, storage_object.uuid),
            }

            self._respond(notification, result, event)

        except Exception as e:
            self.log("Error during object storage:", e, type(e), data,
                     lvl=error, exc=True)

    @handler(delete)
    def delete(self, event):
        data, schema, user, client = self._get_args(event)

        if True:  # try:
            uuid = data['uuid']

            if schema in objectmodels.keys():
                self.log("Looking for object to be deleted.", lvl=debug)
                storage_object = objectmodels[schema].find_one({'uuid': uuid})
                self.log("Found object.", lvl=debug)

                if not self._check_permissions(user, 'write', storage_object):
                    self._cancel_by_permission(schema, data, client)
                    return

                self.log("Fields:", storage_object._fields, "\n\n\n",
                         storage_object.__dict__)
                storage_object.delete()

                self.log("Preparing notification.", lvl=debug)
                notification = objectdeletion(uuid, schema, client)

                if uuid in self.subscriptions:
                    deletion = {
                        'component': 'hfos.events.objectmanager',
                        'action': 'deletion',
                        'data': uuid
                    }
                    for recipient in self.subscriptions[uuid]:
                        self.fireEvent(send(recipient, deletion))

                    del (self.subscriptions[uuid])

                result = {
                    'component': 'hfos.events.objectmanager',
                    'action': 'delete',
                    'data': (True, schema, storage_object.uuid),
                }

                self._respond(notification, result, event)
            else:
                self.log("Unknown schema encountered: ", schema, lvl=warn)
                # except Exception as e:
                #    self.log("Error during delete request: ", e, type(e),
                # lvl=error)

    @handler(subscribe)
    def subscribe(self, event):
        uuid = event.data

        if uuid in self.subscriptions:
            if event.client.uuid not in self.subscriptions[uuid]:
                self.subscriptions[uuid].append(event.client.uuid)
        else:
            self.subscriptions[uuid] = [event.client.uuid]

        result = {
            'component': 'hfos.events.objectmanager',
            'action': 'subscribe',
            'data': {
                'uuid': uuid, 'success': True
            }
        }
        self._respond(None, result, event)

    @handler(unsubscribe)
    def unsubscribe(self, event):
        # TODO: Automatic Unsubscription
        uuid = event.data

        if uuid in self.subscriptions:
            self.subscriptions[uuid].remove(event.client.uuid)

            if len(self.subscriptions[uuid]) == 0:
                del (self.subscriptions[uuid])

        result = {
            'component': 'hfos.events.objectmanager',
            'action': 'unsubscribe',
            'data': {
                'uuid': uuid, 'success': True
            }
        }

        self._respond(None, result, event)

    def update_subscriptions(self, event):
        """OM event handler for to be stored and client shared objectmodels
        :param event: OMRequest with uuid, schema and object data
        """

        self.log("Event: '%s'" % event.__dict__)
        try:
            data = event.data
            self._update_subscribers(data)

        except Exception as e:
            self.log("Error during subscription update: ", type(e), e,
                     exc=True)

    def _update_subscribers(self, updateobject):
        # Notify frontend subscribers

        self.log('Notifying subscribers about update.', lvl=debug)
        if updateobject.uuid in self.subscriptions:
            update = {
                'component': 'hfos.events.objectmanager',
                'action': 'update',
                'data': updateobject.serializablefields()
            }

            for recipient in self.subscriptions[updateobject.uuid]:
                self.log('Notifying subscriber: ', recipient, lvl=verbose)
                self.fireEvent(send(recipient, update))

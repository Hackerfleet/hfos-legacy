"""

Provisioning: Basic Functionality
=================================

Contains
--------

Basic functionality around provisioning.

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from jsonschema import ValidationError
from hfos.logger import hfoslog, debug, verbose, warn, error
from hfos.database import objectmodels

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

system_user = None


def provisionList(items, dbobject, overwrite=False, clear=False,
                  indices=None):
    """Provisions a list of items according to their schema

    :param items: A list of provisionable items.
    :param dbobject: A warmongo database object
    :param overwrite: Causes existing items to be overwritten
    :param clear: Clears the collection first (Danger!)
    :param indices: Creates indices for the given fields
    :return:
    """

    def get_system_user():
        global system_user

        if system_user is None:
            system_user = objectmodels['user'].find_one({'name': 'System'})
            try:
                hfoslog('System user uuid: ', system_user.uuid, lvl=verbose)
            except AttributeError:
                hfoslog('No system user found.')

        return system_user

    # TODO: Do not check this on specific objects but on the model (i.e. once)
    def needs_owner(obj):
        for privilege in obj._fields.get('perms', None):
            if 'owner' in obj._fields['perms'][privilege]:
                return True

        return False

    import pymongo

    # TODO: Fix this to make use of the dbhost

    client = pymongo.MongoClient(host="localhost", port=27017)
    db = client["hfos"]

    col_name = dbobject.collection_name()

    if clear is True:
        hfoslog("Clearing collection for", col_name, lvl=warn,
                emitter='PROVISIONS')
        db.drop_collection(col_name)
    counter = 0

    for no, item in enumerate(items):
        new_object = None
        item_uuid = item['uuid']
        hfoslog("Validating object (%i/%i):" % (no + 1, len(items)), item_uuid,
                emitter='PROVISIONS', lvl=debug)

        if dbobject.count({'uuid': item_uuid}) > 0:
            hfoslog('Object already present', lvl=warn)
            if overwrite is False:
                hfoslog("Not updating item", item, lvl=warn,
                        emitter='PROVISIONS')
            else:
                hfoslog("Overwriting item: ", item_uuid, lvl=warn)
                new_object = dbobject.find_one({'uuid': item_uuid})
                new_object._fields.update(item)
        else:
            new_object = dbobject(item)

        if new_object is not None:
            try:
                if needs_owner(new_object):
                    if not hasattr(new_object, 'owner'):
                        hfoslog('Adding system owner to object.', lvl=verbose)
                        new_object.owner = get_system_user().uuid
            except Exception as e:
                hfoslog('Error during ownership test:', e, type(e),
                        exc=True, lvl=error)
            try:
                new_object.validate()
                new_object.save()
                counter += 1
            except ValidationError as e:
                raise ValidationError(
                    "Could not provision object: " + str(item_uuid), e)

    if indices is not None:
        col = db[col_name]
        for item in indices:
            col.ensure_index([(item, pymongo.TEXT)], unique=True)

            # for index in col.list_indexes():
            #    hfoslog("Index: ", index, emitter='PROVISIONS')

    hfoslog("Provisioned %i out of %i items successfully." % (counter,
                                                              len(items)),
            emitter='PROVISIONS')

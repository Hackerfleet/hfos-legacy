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
from hfos.logger import hfoslog, warn, debug, error
from hfos.database import objectmodels

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


def provisionList(items, dbobject, overwrite=False, clear=False,
                  indexes=None):
    """Provisions a list of items according to their schema
    :param items: A list of provisionable items.
    :param dbobject: A warmongo database object
    """

    systemuser = objectmodels['user'].find_one({'name': 'System'})
    try:
        hfoslog('System user uuid: ', systemuser.uuid)
    except AttributeError:
        hfoslog('No system user found.')

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

    if clear:
        hfoslog("Clearing collection for", col_name, lvl=warn,
                emitter='PROVISIONS')
        db.drop_collection(col_name)
    counter = 0

    for no, item in enumerate(items):
        newobject = None
        itemuuid = item['uuid']
        hfoslog("Validating object (%i/%i):" % (no + 1, len(items)), itemuuid,
                emitter='PROVISIONS', lvl=debug)

        if dbobject.count({'uuid': itemuuid}) > 0:
            if not overwrite:
                hfoslog("Not updating item", item, lvl=warn,
                        emitter='PROVISIONS')
            else:
                hfoslog("Overwriting item: ", itemuuid, lvl=warn)
                newobject = dbobject.find_one({'uuid': itemuuid})
                newobject._fields.update(item)
        else:
            newobject = dbobject(item)

        if newobject is not None:
            try:
                if needs_owner(newobject):
                    if not hasattr(newobject, 'owner'):
                        hfoslog('Adding system owner to object.', lvl=warn)
                        newobject.owner = systemuser.uuid
            except Exception as e:
                hfoslog('Error during ownership test:', e, type(e),
                        exc=True, lvl=error)
            try:
                newobject.validate()
                newobject.save()
                counter += 1
            except ValidationError as e:
                raise ValidationError(
                    "Could not provision object: " + str(itemuuid), e)

    if indexes is not None:
        col = db[col_name]
        for item in indexes:
            col.ensure_index([(item, pymongo.TEXT)], unique=True)

            # for index in col.list_indexes():
            #    hfoslog("Index: ", index, emitter='PROVISIONS')

    hfoslog("Provisioned %i out of %i items successfully." % (counter,
                                                              len(items)),
            emitter='PROVISIONS')

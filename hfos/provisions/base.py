"""

Provisioning: Basic Functionality
=================================

Contains
--------

Basic functionality around provisioning.

:copyright: (C) 2011-2016 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from jsonschema import ValidationError
from hfos.logger import hfoslog, warn
from hfos import database

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

database.initialize()


def provisionList(items, dbobject, overwrite=False, clear=False, indexes=None):
    """Provisions a list of items according to their schema
    :param items: A list of provisionable items.
    :param dbobject: A warmongo database object
    """

    import pymongo

    client = pymongo.MongoClient(host="localhost", port=27017)
    db = client["hfos"]

    col_name = dbobject.collection_name()

    if clear:
        hfoslog("Clearing collection for", col_name, lvl=warn,
                emitter='PROVISIONS')
        db.drop_collection(col_name)
    counter = 0

    for item in items:
        itemuuid = item['uuid']
        hfoslog("Provisioning: Validating object:", itemuuid,
                emitter='PROVISIONS')

        if dbobject.count({'uuid': itemuuid}) > 0 and not overwrite:
            hfoslog("Provisioning: Not updating item", item, lvl=warn,
                    emitter='PROVISIONS')
        else:
            newobject = dbobject(item)

            try:
                newobject.validate()
                newobject.save()
                counter += 1
            except ValidationError as e:
                raise ValidationError(
                    "Could not provision layerobject: " + str(itemuuid), e)

    if indexes is not None:
        col = db[col_name]
        for item in indexes:
            col.ensure_index([(item, pymongo.TEXT)], unique=True)

        for index in col.list_indexes():
            hfoslog("Index: ", index, emitter='PROVISIONS')

    hfoslog("Provisioned %i out of %i items successfully." % (counter,
                                                              len(items)),
            emitter='PROVISIONS')

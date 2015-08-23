"""

Provisioning: Basic Functionality
=================================

Contains
--------

Basic functionality around provisioning.

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from jsonschema import ValidationError

from hfos.logger import hfoslog, warn


def provisionList(items, dbobject, overwrite=False, clear=False):
    """Provisions a list of items according to their schema
    :param items: A list of provisionable items.
    :param dbobject: A warmongo database object
    """

    if clear:
        col_name = dbobject.collection_name()
        hfoslog('[PROV] Clearing collection for', col_name, lvl=warn)

        import pymongo

        client = pymongo.MongoClient(host="localhost", port=27017)
        db = client["hfos"]

        db.drop_collection(col_name)



    for item in items:
        itemname = item['name']
        hfoslog('[PROV] Provisioning: Validating object: ', itemname)

        if dbobject.count({'name': itemname}) > 0 and not overwrite:
            hfoslog('[PROV] Provisioning: Not updating item ', item, lvl=warn)
        else:
            newobject = dbobject(item)

            try:
                newobject.validate()
                newobject.save()
            except ValidationError as e:
                raise ValidationError("Could not provision layerobject: " + str(itemname), e)

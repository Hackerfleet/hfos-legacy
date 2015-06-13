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


def provisionList(items, dbobject):
    """Provisions a list of items according to their schema"""

    for item in items:
        itemname = item['name']
        hfoslog('Provisioning: Validating object: ', itemname)

        if dbobject.count({'name': itemname}) > 0:
            hfoslog('Provisioning: Not updating item ', item, lvl=warn)
        else:
            newobject = dbobject(item)

            try:
                newobject.validate()
                newobject.save()
            except ValidationError as e:
                raise ValidationError("Could not provision layerobject: " + str(itemname), e)

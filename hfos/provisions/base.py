__author__ = 'riot'

from jsonschema import ValidationError

from hfos.logger import hfoslog, warn


def provisionList(items, dbobject):
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
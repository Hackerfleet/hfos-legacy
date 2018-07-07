#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2018 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

"""

Provisioning: Basic Functionality
=================================

Contains
--------

Basic functionality around provisioning.


"""

from jsonschema import ValidationError
from hfos.logger import hfoslog, debug, verbose, warn, error


def log(*args, **kwargs):
    """Log as Emitter:MANAGE"""

    kwargs.update({'emitter': 'PROVISIONS', 'frame_ref': 2})
    hfoslog(*args, **kwargs)


def provisionList(items, database_name, overwrite=False, clear=False, skip_user_check=False):
    """Provisions a list of items according to their schema

    :param items: A list of provisionable items.
    :param database_object: A warmongo database object
    :param overwrite: Causes existing items to be overwritten
    :param clear: Clears the collection first (Danger!)
    :param skip_user_check: Skips checking if a system user is existing already (for user provisioning)
    :return:
    """

    log('Provisioning', items, database_name, lvl=debug)
    system_user = None

    def get_system_user():
        """Retrieves the node local system user"""

        user = objectmodels['user'].find_one({'name': 'System'})

        try:
            log('System user uuid: ', user.uuid, lvl=verbose)
            return user.uuid
        except AttributeError as e:
            log('No system user found:', e, lvl=warn)
            log('Please install the user provision to setup a system user or check your database configuration',
                lvl=error)
            return False

    # TODO: Do not check this on specific objects but on the model (i.e. once)
    def needs_owner(obj):
        """Determines whether a basic object has an ownership field"""
        for privilege in obj._fields.get('perms', None):
            if 'owner' in obj._fields['perms'][privilege]:
                return True

        return False

    import pymongo
    from hfos.database import objectmodels, dbhost, dbport, dbname

    database_object = objectmodels[database_name]

    log(dbhost, dbname)
    # TODO: Fix this to make use of the dbhost

    client = pymongo.MongoClient(dbhost, dbport)
    db = client[dbname]

    if not skip_user_check:
        system_user = get_system_user()

        if not system_user:
            return
    else:
        # TODO: Evaluate what to do instead of using a hardcoded UUID
        # This is usually only here for provisioning the system user
        # One way to avoid this, is to create (instead of provision)
        # this one upon system installation.
        system_user = '0ba87daa-d315-462e-9f2e-6091d768fd36'

    col_name = database_object.collection_name()

    if clear is True:
        log("Clearing collection for", col_name, lvl=warn)
        db.drop_collection(col_name)
    counter = 0

    for no, item in enumerate(items):
        new_object = None
        item_uuid = item['uuid']
        log("Validating object (%i/%i):" % (no + 1, len(items)), item_uuid, lvl=debug)

        if database_object.count({'uuid': item_uuid}) > 0:
            log('Object already present', lvl=warn)
            if overwrite is False:
                log("Not updating item", item, lvl=warn)
            else:
                log("Overwriting item: ", item_uuid, lvl=warn)
                new_object = database_object.find_one({'uuid': item_uuid})
                new_object._fields.update(item)
        else:
            new_object = database_object(item)

        if new_object is not None:
            try:
                if needs_owner(new_object):
                    if not hasattr(new_object, 'owner'):
                        log('Adding system owner to object.', lvl=verbose)
                        new_object.owner = system_user
            except Exception as e:
                log('Error during ownership test:', e, type(e),
                    exc=True, lvl=error)
            try:
                new_object.validate()
                new_object.save()
                counter += 1
            except ValidationError as e:
                raise ValidationError(
                    "Could not provision object: " + str(item_uuid), e)

    log("Provisioned %i out of %i items successfully." % (counter, len(items)))

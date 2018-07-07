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

import json
import sys

import click

from hfos.logger import warn, error
from hfos.tool import log
from hfos.tool.database import db


@db.group()
@click.option("--schema", "-s", default=None, help="Specify object schema to modify")
@click.option("--filter", "-f", "--object-filter", default=None, help="Filter objects (pymongo query syntax)")
@click.option("--action", "-a", default=None, help="Specify action to modify")
@click.option("--role", "-r", default=None, help="Specify role")
@click.option("--all", "--all-schemata", default=False, is_flag=True,
              help="Agree to work on all documents, if no schema specified")
@click.pass_context
def rbac(ctx, schema, object_filter, action, role, all_schemata):
    """Database operations around role based access control."""

    database = ctx.obj['db']

    if schema is None:
        if all_schemata is False:
            log('No schema given. Read the RBAC group help', lvl=warn)
            sys.exit()
        else:
            schemata = database.objectmodels.keys()
    else:
        schemata = [schema]

    things = []

    if object_filter is None:
        parsed_filter = {}
    else:
        parsed_filter = json.loads(object_filter)

    for schema in schemata:
        for obj in database.objectmodels[schema].find(parsed_filter):
            things.append(obj)

    if len(things) == 0:
        log('No objects matched the criteria.', lvl=warn)
        sys.exit()

    ctx.obj['objects'] = things
    ctx.obj['action'] = action
    ctx.obj['role'] = role


@rbac.command(short_help='Add role to action')
@click.pass_context
def add_action_role(ctx):
    """Adds a role to an action on objects"""

    objects = ctx.obj['objects']
    action = ctx.obj['action']
    role = ctx.obj['role']

    if action is None or role is None:
        log('You need to specify an action or role to the RBAC command group for this to work.', lvl=warn)
        return

    for item in objects:
        if role not in item.perms[action]:
            item.perms[action].append(role)
            item.save()

    log("Done")


@rbac.command(short_help='Add role to action')
@click.pass_context
def del_action_role(ctx):
    """Deletes a role from an action on objects"""

    objects = ctx.obj['objects']
    action = ctx.obj['action']
    role = ctx.obj['role']

    if action is None or role is None:
        log('You need to specify an action or role to the RBAC command group for this to work.', lvl=warn)
        return

    for item in objects:
        if role in item.perms[action]:
            item.perms[action].remove(role)
            item.save()

    log("Done")


@rbac.command(short_help='Change owner')
@click.argument('owner')
@click.option("--uuid", help="Specify user by uuid", default=False, is_flag=True)
@click.pass_context
def change_owner(ctx, owner, uuid):
    """Changes the ownership of objects"""

    objects = ctx.obj['objects']
    database = ctx.obj['db']

    if uuid is True:
        owner_filter = {'uuid': owner}
    else:
        owner_filter = {'name': owner}

    owner = database.objectmodels['user'].find_one(owner_filter)
    if owner is None:
        log('User unknown.', lvl=error)
        return

    for item in objects:
        item.owner = owner.uuid
        item.save()

    log('Done')
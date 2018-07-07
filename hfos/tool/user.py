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

from uuid import uuid4

import click
from click_didyoumean import DYMGroup

from hfos.logger import warn
from hfos.misc import std_now
from hfos.tool import _get_credentials, log, _ask
from hfos.tool.database import db


@db.group(cls=DYMGroup)
@click.option("--username", help="Username for user related operations",
              default=None)
@click.option("--password", help="Password for user related operations - supplying this via argument is unsafe",
              default=None)
@click.pass_context
def user(ctx, username, password):
    """User management operations (GROUP)"""

    ctx.obj['username'] = username
    ctx.obj['password'] = password


def _create_user(ctx):
    """Internal method to create a normal user"""

    username, passhash = _get_credentials(ctx.obj['username'],
                                          ctx.obj['password'],
                                          ctx.obj['db'])

    if ctx.obj['db'].objectmodels['user'].count({'name': username}) > 0:
        raise KeyError()

    new_user = ctx.obj['db'].objectmodels['user']({
        'uuid': str(uuid4()),
        'created': std_now()
    })

    new_user.name = username
    new_user.passhash = passhash

    return new_user


@user.command(short_help='create new user')
@click.pass_context
def create_user(ctx):
    """Creates a new local user"""

    try:
        new_user = _create_user(ctx)

        new_user.save()
        log("Done")
    except KeyError:
        log('User already exists', lvl=warn)


@user.command(short_help='create new admin')
@click.pass_context
def create_admin(ctx):
    """Creates a new local user and assigns admin role"""

    try:
        admin = _create_user(ctx)
        admin.roles.append('admin')

        admin.save()
        log("Done")
    except KeyError:
        log('User already exists', lvl=warn)


@user.command(short_help='delete user')
@click.option("--yes", "-y", help="Do not ask for confirmation",
              default=False, is_flag=True)
@click.pass_context
def delete_user(ctx, yes):
    """Delete a local user"""

    if ctx.obj['username'] is None:
        username = _ask("Please enter username:")
    else:
        username = ctx.obj['username']

    del_user = ctx.obj['db'].objectmodels['user'].find_one({'name': username})
    if yes or _ask('Confirm deletion', default=False, data_type='bool'):
        try:
            del_user.delete()
            log("Done")
        except AttributeError:
            log('User not found', lvl=warn)
    else:
        log("Cancelled")


@user.command(short_help="change user's password")
@click.pass_context
def change_password(ctx):
    """Change password of an existing user"""

    username, passhash = _get_credentials(ctx.obj['username'],
                                          ctx.obj['password'],
                                          ctx.obj['db'])

    change_user = ctx.obj['db'].objectmodels['user'].find_one({
        'name': username
    })
    if change_user is None:
        log('No such user', lvl=warn)
        return

    change_user.passhash = passhash
    change_user.save()

    log("Done")


@user.command(short_help='list local users')
@click.option('--search', help='Specify a term for searching', default=None,
              metavar='<text>')
@click.option('--uuid', help='Print user''s uuid as well',
              default=False, is_flag=True)
@click.option('--active', help='Print user''s account activation status',
              default=False, is_flag=True)
@click.pass_context
def list_users(ctx, search, uuid, active):
    """List all locally known users"""

    users = ctx.obj['db'].objectmodels['user']

    for found_user in users.find():
        if not search or (search and search in found_user.name):
            # TODO: Not 2.x compatible
            print(found_user.name, end=' ' if active or uuid else '\n')
            if uuid:
                print(found_user.uuid, end=' ' if active else '\n')
            if active:
                print(found_user.active)

    log("Done")


@user.command(short_help='disable a user')
@click.pass_context
def disable(ctx):
    """Disable an existing user"""

    if ctx.obj['username'] is None:
        log('Specify the username with "iso db user --username ..."')
        return

    change_user = ctx.obj['db'].objectmodels['user'].find_one({
        'name': ctx.obj['username']
    })

    change_user.active = False
    change_user.save()
    log('Done')


@user.command(short_help='disable a user')
@click.pass_context
def enable(ctx):
    """Enable an existing user"""

    if ctx.obj['username'] is None:
        log('Specify the username with "iso db user --username ..."')
        return

    change_user = ctx.obj['db'].objectmodels['user'].find_one({
        'name': ctx.obj['username']
    })

    change_user.active = True
    change_user.save()
    log('Done')


@user.command(short_help='add role to user')
@click.option('--role', help='Specifies the new role', metavar='<name>')
@click.pass_context
def add_role(ctx, role):
    """Grant a role to an existing user"""

    if role is None:
        log('Specify the role with --role')
        return
    if ctx.obj['username'] is None:
        log('Specify the username with --username')
        return

    change_user = ctx.obj['db'].objectmodels['user'].find_one({
        'name': ctx.obj['username']
    })
    if role not in change_user.roles:
        change_user.roles.append(role)
        change_user.save()
        log('Done')
    else:
        log('User already has that role!', lvl=warn)
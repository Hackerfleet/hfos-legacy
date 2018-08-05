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

import click
from click_didyoumean import DYMGroup
from warmongo import model_factory

from hfos.tool import log


@click.group(cls=DYMGroup)
@click.pass_context
def config(ctx):
    """[GROUP] Configuration management operations"""

    from hfos import database
    database.initialize(ctx.obj['dbhost'], ctx.obj['dbname'])

    from hfos.schemata.component import ComponentConfigSchemaTemplate
    ctx.obj['col'] = model_factory(ComponentConfigSchemaTemplate)


@config.command(short_help="Delete component configuration")
@click.argument('componentname')
@click.pass_context
def delete(ctx, componentname):
    """Delete an existing component configuration. This will trigger
    the creation of its default configuration upon next restart."""
    col = ctx.obj['col']

    if col.count({'name': componentname}) > 1:
        log('More than one component configuration of this name! Try '
            'one of the uuids as argument. Get a list with "config '
            'list"')
        return

    log('Deleting component configuration', componentname,
        emitter='MANAGE')

    configuration = col.find_one({'name': componentname})

    if configuration is None:
        configuration = col.find_one({'uuid': componentname})

    if configuration is None:
        log('Component configuration not found:', componentname,
            emitter='MANAGE')
        return

    configuration.delete()
    log('Done')


@config.command(short_help="Show component configurations")
@click.option('--component', default=None)
@click.pass_context
def show(ctx, component):
    """Show the stored, active configuration of a component."""

    col = ctx.obj['col']

    if col.count({'name': component}) > 1:
        log('More than one component configuration of this name! Try '
            'one of the uuids as argument. Get a list with "config '
            'list"')
        return

    if component is None:
        configurations = col.find()
        for configuration in configurations:
            log("%-15s : %s" % (configuration.name,
                                configuration.uuid),
                emitter='MANAGE')
    else:
        configuration = col.find_one({'name': component})

        if configuration is None:
            configuration = col.find_one({'uuid': component})

        if configuration is None:
            log('No component with that name or uuid found.')
            return

        print(json.dumps(configuration.serializablefields(), indent=4))
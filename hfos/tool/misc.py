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

import click
from click_repl import repl
from prompt_toolkit.history import FileHistory

from hfos.tool import run_process
from hfos.tool.cli import cli


@cli.command(short_help='Start interactive management shell')
def shell():
    """Open an shell to work with the manage tool interactively."""

    prompt_kwargs = {
        'history': FileHistory('/tmp/.hfos-manage.history'),
    }
    print("""HFOS - Management Tool Interactive Prompt

Type -h for help, tab completion is available, hit Ctrl-D to quit.""")
    repl(click.get_current_context(), prompt_kwargs=prompt_kwargs)


@cli.command(short_help='View command map graph (requires xdot)')
def cmdmap():
    # TODO: Integrate the output into documentation

    from copy import copy

    def print_commands(command, map_output, groups=None):
        if groups is None:
            groups = []
        if 'commands' in command.__dict__:
            if len(groups) > 0:
                map_output.append("    %s -> %s [weight=1.0];\n" % (groups[-1], command.name))

            for item in command.commands.values():
                subgroups = copy(groups)
                subgroups.append(command.name)
                print_commands(item, map_output, subgroups)
        else:
            map_output.append("    %s -> %s [weight=%1.1f];\n" % (groups[-1], command.name, len(groups)))

    with open('iso.dot', 'w') as f:
        f.write('strict digraph {\n')
        output = []
        print_commands(cli, output)
        f.writelines(sorted(output))
        f.write('}')

    run_process('.', ['xdot', 'iso.dot'])
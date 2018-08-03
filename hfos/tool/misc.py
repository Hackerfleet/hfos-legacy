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
@click.option("--xdot", help="Use xdot for nicer displaying", is_flag=True, default=False)
def cmdmap(xdot):
    """Generates a command map"""
    # TODO: Integrate the output into documentation

    from copy import copy

    def print_commands(command, map_output, groups=None, depth=0):
        if groups is None:
            groups = []
        if 'commands' in command.__dict__:
            if len(groups) > 0:
                if xdot:
                    line = "    %s -> %s [weight=1.0];\n" % (groups[-1], command.name)
                else:
                    line = "    " * (depth - 1) + "%s %s\n" % (groups[-1], command.name)
                map_output.append(line)

            for item in command.commands.values():
                subgroups = copy(groups)
                subgroups.append(command.name)
                print_commands(item, map_output, subgroups, depth + 1)
        else:
            if xdot:
                line = "    %s -> %s [weight=%1.1f];\n" % (groups[-1], command.name, len(groups))
            else:
                line = "    " * (len(groups) - 3 + depth) + "%s %s\n" % (groups[-1], command.name)
            map_output.append(line)

    output = []
    print_commands(cli, output)

    output = [line.replace("cli", "isomer") for line in output]

    if xdot:
        with open('iso.dot', 'w') as f:
            f.write('strict digraph {\n')
            f.writelines(sorted(output))
            f.write('}')

        run_process('.', ['xdot', 'iso.dot'])
    else:
        print("".join(output))

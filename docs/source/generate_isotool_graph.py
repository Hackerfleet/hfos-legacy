#!/usr/bin/env python

from copy import copy

def print_commands(command, output, groups=[]):
    if 'commands' in command.__dict__:
        if len(groups) > 0:
            output.append("    %s -> %s [weight=1.0];" % (groups[-1], command.name))

        for item in command.commands.values():
            subgroups = copy(groups)
            subgroups.append(command.name)
            print_commands(item, output, subgroups)
    else:
        output.append("    %s -> %s [weight=%1.1f];" % (groups[-1], command.name, len(groups)))


with open('iso.dot', 'w') as f:
    f.write('strict digraph {\n')
    output = []
    print_commands(cli, output)
    f.writelines(output)
    f.write('}')

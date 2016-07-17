#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System - Dev Plugin
# =================================================
# Copyright (C) 2011-2016 riot <riot@hackerfleet.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import shutil
import argparse
from time import localtime
from pprint import pprint
from collections import OrderedDict
from templates import writeTemplateFile

paths = [
    'hfos',
    'hfos/{pluginname}',
    'hfos-frontend/{pluginname}/scripts/controllers',
    'hfos-frontend/{pluginname}/views'
]

templates = {
    'setupfile': ('setup.py.template', 'setup.py'),
    'packagefile': ('package.json.template', 'package.json'),
    'component': (
    'component.py.template', 'hfos/{pluginname}/{pluginname}.py'),
    'moduleinit': ('init.py.template', 'hfos/__init__.py'),
    'packageinit': ('init.py.template', 'hfos/{pluginname}/__init__.py'),
    'schemata': ('schemata.py.template', 'hfos/{pluginname}/schemata.py'),
    'controller': ('controller.js.template',
                   'hfos-frontend/{pluginname}/scripts/controllers/{'
                   'pluginname}.js'),
    'view': (
    'view.html.template', 'hfos-frontend/{pluginname}/views/{pluginname}.html')
}

questions = OrderedDict({
    'pluginname': 'plugin',
    'authorname': u'author',
    'authoremail': u'author@domain.tld',
    'description': u'Description',
    'longdescription': u'Very long description, use \\n to get multilines.',
    'version': '0.0.1',
    'githuburl': 'hackerfleet/example',
    'license': 'GPLv3',
    'keywords': u'hfos example plugin'

})

infoheader = """The manage command guides you through setting up a new HFOS
package.
It provides basic setup. If you need dependencies or have other special
needs, edit the resulting
files by hand.

You can press Ctrl-C any time to cancel this process.

See hfos_manage --help for more details.
"""


def augment_info(info):
    info['descriptionheader'] = "=" * len(info['description'])
    info['componentname'] = info['pluginname'].capitalize()
    info['year'] = localtime().tm_year
    info['licenselongtext'] = ''

    info['keywordlist'] = ""
    for keyword in info['keywords'].split(" "):
        info['keywordlist'] += "'" + keyword + "', "
    if len(info['keywordlist']) > 0:
        # strip last comma
        info['keywordlist'] = info['keywordlist'][:-2]

    return info


def construct_module(info, target):
    for path in paths:
        realpath = os.path.abspath(os.path.join(target, path.format(**info)))
        print("Making directory '%s'" % realpath)
        os.makedirs(realpath)

    # pprint(info)
    for template, item in templates.items():
        source = os.path.join('templates', item[0])
        filename = os.path.abspath(
            os.path.join(target, item[1].format(**info)))
        print("Creating file from template '%s'" % filename)
        writeTemplateFile(source, filename, info)


def ask(question, default=None, datatype=str):
    data = default

    if datatype == bool:
        data = None
        while data not in ('Y', 'J', 'N', '1', '0'):
            data = raw_input(
                "%s? [%s]: " % (question, default.upper())).upper()

            if default and data == '':
                return default

        return data in ('Y', 'J', '1')

    elif datatype in (str, unicode):
        data = raw_input("%s? [%s] (%s): " % (question, default, datatype))

        if len(data) == 0:
            data = default

    return data


def askquestionnaire():
    answers = {}
    print(infoheader)
    pprint(questions.items())

    for question, default in questions.items():
        response = ask(question, default, type(default))
        if type(default) == unicode:
            response = response.decode('utf-8')
        answers[question] = response

    return answers


def main(args):
    if os.path.exists(args.target):
        if args.clear:
            shutil.rmtree(args.target)
        else:
            print("Target exists! Use --clear to delete it first.")
            sys.exit(-1)

    done = False
    info = None

    while not done:
        info = askquestionnaire()
        pprint(info)
        done = ask('Is the above correct?', default='y', datatype=bool)

    augmentedinfo = augment_info(info)

    print("Constructing module %(pluginname)s" % info)
    construct_module(augmentedinfo, args.target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target",
                        help="Create module in the given folder (uses ./ if "
                             "omitted)",
                        action="store",
                        default=".")
    parser.add_argument("--clear", help="Clear target path if it exists",
                        action="store_true", default=False)

    args = parser.parse_args()

    main(args)

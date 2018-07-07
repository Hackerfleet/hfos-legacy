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

import sys
import time
from pprint import pprint

import click
import os
import shutil
from collections import OrderedDict

from hfos.tool import log, _ask
from hfos.tool.templates import write_template_file

try:
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    unicode  # NOQA
except NameError:
    unicode = str

paths = [
    'hfos',
    'hfos/{plugin_name}',
    'hfos-frontend/{plugin_name}/scripts/controllers',
    'hfos-frontend/{plugin_name}/views'
]

templates = {
    'setup_file': ('setup.py.template', 'setup.py'),
    'package_file': ('package.json.template', 'package.json'),
    'component': (
        'component.py.template', 'hfos/{plugin_name}/{plugin_name}.py'),
    'module_init': ('init.py.template', 'hfos/__init__.py'),
    'package_init': ('init.py.template', 'hfos/{plugin_name}/__init__.py'),
    'schemata': ('schemata.py.template', 'hfos/{plugin_name}/schemata.py'),
    'controller': ('controller.js.template',
                   'hfos-frontend/{plugin_name}/scripts/controllers/{'
                   'plugin_name}.js'),
    'view': (
        'view.html.template',
        'hfos-frontend/{plugin_name}/views/{plugin_name}.html')
}

questions = OrderedDict({
    'plugin_name': 'plugin',
    'author_name': u'author',
    'author_email': u'author@domain.tld',
    'description': u'Description',
    'long_description': u'Very long description, use \\n to get multilines.',
    'version': '0.0.1',
    'github_url': 'hackerfleet/example',
    'license': 'GPLv3',
    'keywords': 'hfos example plugin'

})

info_header = """The manage command guides you through setting up a new HFOS
package.
It provides basic setup. If you need dependencies or have other special
needs, edit the resulting files by hand.

You can press Ctrl-C any time to cancel this process.

See hfos_manage --help for more details.
"""


def _augment_info(info):
    """Fill out the template information"""

    info['description_header'] = "=" * len(info['description'])
    info['component_name'] = info['plugin_name'].capitalize()
    info['year'] = time.localtime().tm_year
    info['license_longtext'] = ''

    info['keyword_list'] = u""
    for keyword in info['keywords'].split(" "):
        print(keyword)
        info['keyword_list'] += u"\'" + str(keyword) + u"\', "
    print(info['keyword_list'])
    if len(info['keyword_list']) > 0:
        # strip last comma
        info['keyword_list'] = info['keyword_list'][:-2]

    return info


def _construct_module(info, target):
    """Build a module from templates and user supplied information"""

    for path in paths:
        real_path = os.path.abspath(os.path.join(target, path.format(**info)))
        log("Making directory '%s'" % real_path)
        os.makedirs(real_path)

    # pprint(info)
    for item in templates.values():
        source = os.path.join('dev/templates', item[0])
        filename = os.path.abspath(
            os.path.join(target, item[1].format(**info)))
        log("Creating file from template '%s'" % filename,
            emitter='MANAGE')
        write_template_file(source, filename, info)


def _ask_questionnaire():
    """Asks questions to fill out a HFOS plugin template"""

    answers = {}
    print(info_header)
    pprint(questions.items())

    for question, default in questions.items():
        response = _ask(question, default, str(type(default)), show_hint=True)
        if type(default) == unicode and type(response) != str:
            response = response.decode('utf-8')
        answers[question] = response

    return answers


@click.command(short_help='create starterkit module')
@click.option('--clear', '--clear-target', help='Clears already existing target',
              default=False, is_flag=True)
@click.option("--target", help="Create module in the given folder (uses ./ "
                               "if omitted)", default=".", metavar='<folder>')
def create_module(clear_target, target):
    """Creates a new template HFOS plugin module"""

    if os.path.exists(target):
        if clear_target:
            shutil.rmtree(target)
        else:
            log("Target exists! Use --clear to delete it first.",
                emitter='MANAGE')
            sys.exit(2)

    done = False
    info = None

    while not done:
        info = _ask_questionnaire()
        pprint(info)
        done = _ask('Is the above correct', default='y', data_type='bool')

    augmented_info = _augment_info(info)

    log("Constructing module %(plugin_name)s" % info)
    _construct_module(augmented_info, target)

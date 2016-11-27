#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System - Dev Plugin
# =================================================
# Copyright (C) 2011-2016 riot <riot@c-base.org> and others.
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
from templates import write_template_file
from hashlib import sha512

# TODO: Must be synchronized with hfos.ui.auth.Authenticator.salt!
# Currently this is set to a static value (no good, but better than nothing)

try:
    salt = 'FOOBAR'.encode('utf-8')
except UnicodeEncodeError:
    salt = u'FOOBAR'

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
        'view.html.template',
        'hfos-frontend/{pluginname}/views/{pluginname}.html')
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

try:
    input = raw_input  # NOQA
except NameError:
    pass

try:
    unicode  # NOQA
except NameError:
    unicode = str


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
    for item in templates.values():
        source = os.path.join('dev/templates', item[0])
        filename = os.path.abspath(
            os.path.join(target, item[1].format(**info)))
        print("Creating file from template '%s'" % filename)
        write_template_file(source, filename, info)


def ask(question, default=None, datatype=str, showhint=False):
    data = default

    if datatype == bool:
        data = None
        while data not in ('Y', 'J', 'N', '1', '0'):
            data = input(
                "%s? [%s]: " % (question, default.upper())).upper()

            if default and data == '':
                return default

        return data in ('Y', 'J', '1')

    elif datatype in (str, unicode):
        if showhint:
            msg = "%s? [%s] (%s): " % (question, default, datatype)
        else:
            msg = question

        data = input(msg)

        if len(data) == 0:
            data = default

    return data


def askquestionnaire():
    answers = {}
    print(infoheader)
    pprint(questions.items())

    for question, default in questions.items():
        response = ask(question, default, type(default), showhint=True)
        if type(default) == unicode:
            response = response.decode('utf-8')
        answers[question] = response

    return answers


def create_module(args):
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


def ask_password():
    password = "Foo"
    password_trial = ""

    while password != password_trial:
        password = ask("Enter password: ")
        password_trial = ask("Repeat password: ")
        if password != password_trial:
            print("\nPasswords do not match!")

    return password


def get_credentials(args):
    if not args.username:
        username = ask("Please enter username: ")
    else:
        username = args.username

    if not args.password:
        password = ask_password()
    else:
        password = args.password

    try:
        password = password.encode('utf-8')
    except UnicodeDecodeError:
        password = password

    passhash = sha512(password)
    passhash.update(salt)

    return username, passhash.hexdigest()


def create_user(args):
    username, passhash = get_credentials(args)


def delete_user(args):
    if not args.username:
        username = ask("Please enter username: ")
    else:
        username = args.username

    from hfos import database

    database.initialize(args.dbhost)

    user = database.objectmodels['user'].find_one({'name': username})
    # TODO: Verify back if not --yes in args
    user.delete()

    print("Done!")


def change_password(args):
    username, passhash = get_credentials(args)

    from hfos import database

    database.initialize(args.dbhost)

    user = database.objectmodels['user'].find_one({'name': username})

    user.passhash = passhash
    user.save()

    print("Done!")


def list_users(args):
    from hfos import database

    database.initialize(args.dbhost)

    users = database.objectmodels['user']

    for user in users.find():
        print(user.name, user.uuid)

    print("Done!")


def main(args, parser):
    # TODO: This can be done better. Re-find out how and change.
    if args.create_module:
        create_module(args)
    elif args.create_user:
        create_user(args)
    elif args.delete_user:
        delete_user(args)
    elif args.change_password:
        change_password(args)
    elif args.list_users:
        list_users(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target",
                        help="Create module in the given folder (uses ./ if "
                             "omitted)",
                        action="store",
                        default=".")
    parser.add_argument("--clear", help="Clear target path if it exists",
                        action="store_true", default=False)
    parser.add_argument("--username", help="Username for user related "
                                           "operations", default=None)
    parser.add_argument("--password", help="Password for user related "
                                           "operations", default=None)
    parser.add_argument("--dbhost", help="Define hostname for database server",
                        type=str, default='127.0.0.1:27017')

    parser.add_argument("-create-module", help="Create a new module",
                        action="store_true", default=False)

    parser.add_argument("-list-users", help="List all existing user accounts",
                        action="store_true", default=False)
    parser.add_argument("-create-user", help="Create a new user",
                        action="store_true", default=False)
    parser.add_argument("-delete-user", help="Delete an existing user account",
                        action="store_true", default=False)
    parser.add_argument("-change-password",
                        help="Change password of existing user",
                        action="store_true", default=False)

    args = parser.parse_args()

    main(args, parser)

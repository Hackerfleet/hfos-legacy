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
from distutils.dir_util import copy_tree
from time import localtime
from pprint import pprint
from collections import OrderedDict
from dev.templates import write_template_file
from hashlib import sha512

from hfos.ui.builder import install_frontend
from hfos.logger import verbose, debug, warn, error, critical, verbosity, \
    hfoslog

# 2.x/3.x imports: (TODO: Simplify those, one 2x/3x ought to be enough)
try:
    input = raw_input  # NOQA
except NameError:
    pass

try:
    from subprocess import Popen
except ImportError:
    from subprocess32 import Popen  # NOQA

try:
    unicode  # NOQA
except NameError:
    unicode = str

# Database salt
try:
    # TODO: Must be synchronized with hfos.ui.auth.Authenticator.salt!
    # Currently this is set to a static value (no good,but better than nothing)
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
    'keywords': 'hfos example plugin'

})

infoheader = """The manage command guides you through setting up a new HFOS
package.
It provides basic setup. If you need dependencies or have other special
needs, edit the resulting files by hand.

You can press Ctrl-C any time to cancel this process.

See hfos_manage --help for more details.
"""


def augment_info(info):
    info['descriptionheader'] = "=" * len(info['description'])
    info['componentname'] = info['pluginname'].capitalize()
    info['year'] = localtime().tm_year
    info['licenselongtext'] = ''

    info['keywordlist'] = u""
    for keyword in info['keywords'].split(" "):
        print(keyword)
        info['keywordlist'] += u"\'" + str(keyword) + u"\', "
    print(info['keywordlist'])
    if len(info['keywordlist']) > 0:
        # strip last comma
        info['keywordlist'] = info['keywordlist'][:-2]

    return info


def construct_module(info, target):
    for path in paths:
        realpath = os.path.abspath(os.path.join(target, path.format(**info)))
        hfoslog("Making directory '%s'" % realpath, emitter='MANAGE')
        os.makedirs(realpath)

    # pprint(info)
    for item in templates.values():
        source = os.path.join('dev/templates', item[0])
        filename = os.path.abspath(
            os.path.join(target, item[1].format(**info)))
        hfoslog("Creating file from template '%s'" % filename,
                emitter='MANAGE')
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
        if type(default) == unicode and type(response) != str:
            response = response.decode('utf-8')
        answers[question] = response

    return answers


def create_module(args):
    if os.path.exists(args.target):
        if args.clear:
            shutil.rmtree(args.target)
        else:
            hfoslog("Target exists! Use --clear to delete it first.",
                    emitter='MANAGE')
            sys.exit(-1)

    done = False
    info = None

    while not done:
        info = askquestionnaire()
        pprint(info)
        done = ask('Is the above correct', default='y', datatype=bool)

    augmentedinfo = augment_info(info)

    hfoslog("Constructing module %(pluginname)s" % info, emitter='MANAGE')
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

    from hfos import database
    from uuid import uuid4
    database.initialize(args.dbhost)

    user = database.objectmodels['user']()

    user.uuid = str(uuid4())
    user.name = username
    user.passhash = passhash
    user.save()

    hfoslog("Done!", emitter='MANAGE')


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

    hfoslog("Done!", emitter='MANAGE')


def change_password(args):
    username, passhash = get_credentials(args)

    from hfos import database
    database.initialize(args.dbhost)

    user = database.objectmodels['user'].find_one({'name': username})

    user.passhash = passhash
    user.save()

    hfoslog("Done!", emitter='MANAGE')


def list_users(args):
    from hfos import database
    database.initialize(args.dbhost)

    users = database.objectmodels['user']

    for user in users.find():
        print(user.name, user.uuid)

    hfoslog("Done!", emitter='MANAGE')


def install_docs(args):
    def make_docs():
        hfoslog("Generating HTML documentation", emitter='MANAGE')

        try:
            build = Popen(
                [
                    'make',
                    'html'
                ],
                cwd='docs/'
            )

            build.wait()
        except Exception as e:
            hfoslog("Problem during documentation building: ", e, type(e),
                    exc=True, emitter='MANAGE', lvl=error)
            return False
        return True

    make_docs()

    hfoslog("Updating documentation directory", emitter='MANAGE')

    # If these need changes, make sure they are watertight and don't remove
    # wanted stuff!
    target = '/var/lib/hfos/frontend/docs'
    source = 'docs/build/html'

    if not os.path.exists(os.path.join(os.path.curdir, source)):
        hfoslog(
            "Documentation not existing yet. Run python setup.py "
            "build_sphinx first.", emitter='MANAGE', lvl=error)
        return

    if os.path.exists(target):
        hfoslog("Path already exists: " + target, emitter='MANAGE')
        if args.clear:
            hfoslog("Cleaning up " + target, emitter='MANAGE', lvl=warn)
            shutil.rmtree(target)

    hfoslog("Copying docs to " + target, emitter='MANAGE')
    copy_tree(source, target)


def install_var(args):
    hfoslog("Checking frontend library and cache directories",
            emitter='MANAGE')

    # If these need changes, make sure they are watertight and don't remove
    # wanted stuff!
    target_paths = (
        '/var/lib/hfos',
        '/var/cache/hfos',
        '/var/cache/hfos/tilecache',
        '/var/cache/hfos/rastertiles',
        '/var/cache/hfos/rastercache'
    )

    for item in target_paths:
        if os.path.exists(item):
            hfoslog("Path already exists: " + item, emitter='MANAGE')
            if args.clear_all or (args.clear and 'cache' in item):
                hfoslog("Cleaning up: " + item, emitter='MANAGE', lvl=warn)
                shutil.rmtree(item)

        if not os.path.exists(item):
            hfoslog("Creating path: " + item, emitter='MANAGE')
            os.mkdir(item)


def install_provisions(args):
    hfoslog("Installing HFOS default provisions", emitter='MANAGE')

    # from hfos.logger import verbosity, events
    # verbosity['console'] = verbosity['global'] = events

    from hfos.database import initialize

    initialize(args.dbhost)

    from hfos.provisions import provisionstore

    if args.provision is not None and args.provision in provisionstore:
        hfoslog("Provisioning ", args.provision, emitter="MANAGE")
        provisionstore[args.provision]
    elif args.provision is None:
        for provision_name in provisionstore:
            hfoslog("Provisioning " + provision_name, emitter='MANAGE')
            provisionstore[provision_name]()
    else:
        hfoslog("Unknown provision: ", args.provision, "\nValid provisions "
                                                       "are",
                list(provisionstore.keys()),
                lvl=error,
                emitter='MANAGE')


def uninstall(args):
    response = ask("This will delete all data of your HFOS installation! Type"
                   "YES to continue:", default="N", showhint=False)
    if response == 'YES':
        shutil.rmtree('/var/lib/hfos')
        shutil.rmtree('/var/cache/hfos')


def install_modules(args):
    def install_module(module):
        try:
            setup = Popen(
                [
                    'python',
                    'setup.py',
                    'develop'
                ],
                cwd='modules/' + module + "/"
            )

            setup.wait()
        except Exception as e:
            hfoslog("Problem during module installation: ", module, e,
                    type(e), exc=True, emitter='MANAGE', lvl=error)
            return False
        return True

    modules = [
        # Poor man's dependency management, as long as the modules are
        # installed from local sources and they're not available on pypi,
        # which would handle real dependency management for us:
        'navdata',
        'robot',

        # Now all the rest:
        'alert',
        'busrepeater',
        'camera',
        'chat',
        'comms',
        'countables',
        'crew',
        'dash',
        # 'dev',
        'garden',
        'ldap',
        'library',
        'logbook',
        'maps',
        'nmea',
        'polls',
        'project',
        'protocols',
        'shareables',
        'switchboard',
        'wiki'
    ]

    success = []
    failed = []

    for module in modules:
        hfoslog('Installing module ', module, emitter='MANAGE')
        if install_module(module):
            success.append(module)
        else:
            failed.append(module)

    hfoslog('Installed modules: ', success, emitter='MANAGE')
    if len(failed) > 0:
        hfoslog('Failed modules: ', failed, emitter='MANAGE')
    hfoslog('Done!', emitter='MANAGE')


def install_all(args):
    # First install base
    install_var(args)
    install_modules(args)

    # Now the rest basing off that
    install_provisions(args)
    install_docs(args)
    install_frontend(args, forcerebuild=True)


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
    elif args.install_provisions:
        install_provisions(args)
    elif args.install_docs:
        install_docs(args)
    elif args.install_var:
        install_var(args)
    elif args.install_frontend:
        install_frontend(args, forcerebuild=True)
    elif args.install_modules:
        install_modules(args)
    elif args.install_all:
        install_all(args)
    elif args.uninstall:
        uninstall(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    # TODO: See if there's a nicer method to build a command interface than
    # argparser. I think there was some sleek lib to do that.
    parser = argparse.ArgumentParser()

    # TODO: Make use of these two flags where appropriate and bail out with err
    # if they were specified where it is not possible to adhere to them
    parser.add_argument("--quiet", "-q", help="Quiet operation to suppress "
                                              "all output",
                        action="store_true", default=False)
    parser.add_argument("--log", help="Define log level (0-100)",
                        type=int, default=20)
    parser.add_argument("--yes", "-y", help="Assume yes on any yes/no "
                                            "questions",
                        action="store_true", default=False)
    parser.add_argument("--target",
                        help="Create module in the given folder (uses ./ if "
                             "omitted)",
                        action="store",
                        default=".")
    parser.add_argument("--provision",
                        "-p",
                        help="Install only given provision data",
                        action="store",
                        default=None)
    # TODO: Clarify these, make their functions more obvious
    parser.add_argument("--clear", help="Clear target path if it exists",
                        action="store_true", default=False)
    parser.add_argument("--clear-all", help="Clear all target paths if they "
                                            "exist, not only caches",
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
    parser.add_argument("-install-var",
                        help="Install variable data locations",
                        action="store_true", default=False)
    parser.add_argument("-install-docs",
                        help="Install documentation",
                        action="store_true", default=False)
    parser.add_argument("-install-provisions",
                        help="Install system data provisions",
                        action="store_true", default=False)
    parser.add_argument("-install-frontend",
                        help="Install HFOS frontend",
                        action="store_true", default=False)
    parser.add_argument("-install-modules",
                        help="Install all supplied Hackerfleet modules",
                        action="store_true",
                        default=False)
    parser.add_argument("-install-all",
                        help="Install all necessary things",
                        action="store_true",
                        default=False)
    parser.add_argument("-uninstall",
                        help="Delete installed things and clean up",
                        action="store_true",
                        default=False)

    args = parser.parse_args()

    verbosity['console'] = args.log
    verbosity['global'] = args.log

    main(args, parser)

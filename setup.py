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

from setuptools import setup
import os

# TODO:
# Classifiers
# Keywords
# download_url
# platform

ignore = [
    '/frontend/node_modules',
    '/frontend/build',
    '/frontend/src/components',
    '/docs/build',
    '__pycache__'
]
datafiles = []
manifestfiles = []


def prune(thing):
    for part in ignore:
        part = part[1:] if part.startswith('/') else part
        if part in thing:
            return True
    return False


def add_datafiles(*paths):
    manifest = open('MANIFEST.in', 'w')

    for path in paths:
        files = []
        manifest.write('recursive-include ' + path + ' *\n')

        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                datafile = os.path.join(root, filename)

                if not prune(datafile):
                    files.append(datafile)
                    manifestfiles.append(datafile)

        datafiles.append((path, files))

    for part in ignore:
        if part.startswith('/'):
            manifest.write('prune ' + part[1:] + '\n')
        else:
            manifest.write('global-exclude ' + part + '/*\n')


add_datafiles('frontend', 'docs')

setup(name="hfos",
      description="hfos",
      version="1.2.0",
      author="Hackerfleet Community",
      author_email="riot@c-base.org",
      maintainer="Hackerfleet Community",
      maintainer_email="riot@c-base.org",
      url="https://hackerfleet.github.io",
      license="GNU Affero General Public License v3",
      packages=['hfos',
                'hfos.schemata',
                'hfos.ui',
                'hfos.provisions'],
      namespace_packages=['hfos'],
      scripts=[
          'iso',
      ],
      long_description="""HFOS - The Hackerfleet Operating System
=======================================

A modern, opensource approach to maritime navigation.

This software package is supposed to run on your ship/car/plane/ufo's board
computer.
See https://github.com/hackerfleet/hfos""",
      dependency_links=[
          'https://github.com/Hackerfleet/warmongo/archive/master.zip#egg'
          '=warmongo-0.5.5.hf'
      ],
      install_requires=['circuits>=3.1',
                        'pymongo>=3.2',
                        'jsonschema>=2.6.0',
                        'pystache>=0.5.4',
                        'click>=6.7.0',
                        'six'
                        ],
      data_files=datafiles,
      entry_points="""[console_scripts]
    hfos_launcher=hfos.launcher:launch
    hfos_manage=hfos_manage:cli
    
    [hfos.base]
    debugger=hfos.debugger:HFDebugger
    cli=hfos.debugger:CLI
    syslog=hfos.ui.syslog:Syslog
    maintenance=hfos.database:Maintenance
    backup=hfos.database:BackupManager

    [hfos.sails]
    auth=hfos.ui.auth:Authenticator
    clientmanager=hfos.ui.clientmanager:ClientManager
    objectmanager=hfos.ui.objectmanager:ObjectManager
    schemamanager=hfos.ui.schemamanager:SchemaManager
    tagmanager=hfos.ui.tagmanager:TagManager
    configurator=hfos.ui.configurator:Configurator

    [hfos.schemata]
    systemconfig=hfos.schemata.system:Systemconfig
    client=hfos.schemata.client:Client
    profile=hfos.schemata.profile:Profile
    user=hfos.schemata.user:User
    logmessage=hfos.schemata.logmessage:LogMessage
    tag=hfos.schemata.tag:Tag

    [hfos.provisions]
    system=hfos.provisions.system:provision
    user=hfos.provisions.user:provision
    """,
      # use_scm_version={
      #       "write_to": "hfos/version.py",
      # },
      # setup_requires=[
      #       "setuptools_scm"
      # ],
      test_suite="tests.main.main",
      )

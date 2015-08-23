#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2015 riot <riot@hackerfleet.org> and others.
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

from setuptools import setup
from setuptools import Command
from distutils.log import INFO, WARN
from distutils.dir_util import copy_tree

import os
from shutil import rmtree

# TODO:
# Classifiers
# Keywords
# download_url
# platform

class install_doc(Command):
    description = "Installs documentation into frontend library directory"
    user_options = [
        # The format is (long option, short option, description).
        ('clean', None, 'Clear docs first')
    ]

    def initialize_options(self):
        """Set default values for options."""
        self.clean = False

    def finalize_options(self):
        """Post-process options."""

    def run(self):
        self.announce("Updating documentation directory", INFO)

        # If these need changes, make sure they are watertight and don't remove wanted stuff!
        target = '/var/lib/hfos/static/docs'
        source = 'docs/build/html'

        if not os.path.exists(os.path.join(os.path.curdir, source)):
            self.announce("Documentation not existing yet. Run python setup.py build_sphinx first.")
            return

        if os.path.exists(target):
            self.announce("Path already exists: " + target)
            if self.clean:
                self.announce("Cleaning up " + target, WARN)
                rmtree(target)

        self.announce("Copying docs to " + target, INFO)
        copy_tree(source, target)


class install_var(Command):
    description = "Installs frontend library and cache directories"
    user_options = [
        # The format is (long option, short option, description).
        ('clean-all', None, 'Clear frontend and HFOS cache data'),
        ('clean', None, 'Clear HFOS cache')
    ]

    def initialize_options(self):
        """Set default values for options."""
        self.clean_all = False
        self.clean = False

    def finalize_options(self):
        """Post-process options."""

    def run(self):
        self.announce("Checking frontend library and cache directories", INFO)

        # If these need changes, make sure they are watertight and don't remove wanted stuff!
        paths = ('/var/lib/hfos', '/var/cache/hfos', '/var/cache/hfos/tilecache')

        for item in paths:
            if os.path.exists(item):
                self.announce("Path already exists: " + item)
                if self.clean_all or (self.clean and 'cache' in item):
                    self.announce("Cleaning up: " + item, WARN)
                    rmtree(item)

            if not os.path.exists(item):
                self.announce("Creating path: " + item, INFO)
                os.mkdir(item)


setup(name="hfos",
      version="1.0.0",
      description="hfos",

      author="Hackerfleet Community",
      author_email="packages@hackerfleet.org",
      url="https://github.com/hackerfleet/hfos",
      license="GNU General Public License v3",
      packages=['hfos',
                'hfos.schemata',
                'hfos.web',
                'hfos.provisions'],
      scripts=[
          'hfos_launcher.py',
      ],
      cmdclass={
          'install_var': install_var,
          'install_doc': install_doc
      },
      long_description="""HFOS - The Hackerfleet Operating System
=======================================

A modern, opensource approach to maritime navigation.

This software package is supposed to run on your ship/car/plane/ufo's board computer.
See https://github.com/hackerfleet/hfos""",
      dependency_links=[
          'https://github.com/Hackerfleet/warmongo/archive/master.zip#egg=warmongo-0.5.3.hf'
      ],
      install_requires=['circuits==3.1.0',
                        'pymongo>=3.0.3',
                        'jsonschema>=2.5.1',
                        'pynmea2==1.4.0',
                        'warmongo==0.5.3.hf',
                        'six'
                        ],
      test_suite="tests.main.main",
      )

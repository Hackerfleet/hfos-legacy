#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Hackerfleet Technology Demonstrator License
# ===========================================
# Copyright (C) 2011-2014 riot <riot@hackerfleet.org> and others.
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

from setuptools import setup


# TODO: rebuild the package finder using setuptools & pkg_resources

def include_readme():
    readme = open("README.md")
    include = readme.readlines(10)[2:10]
    readme.close()
    return "".join(include)


def is_package(path):
    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py'))
    )


def find_packages(path, base=""):
    """ Find all packages in path """
    packages = {}
    for item in os.listdir(path):
        dir = os.path.join(path, item)
        if is_package(dir):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            packages[module_name] = dir
            packages.update(find_packages(dir, module_name))
    return packages


packages = find_packages(".")
package_names = list(packages.keys())

setup(name="hfos",
      version="1.0.0",
      description="hfos",

      author="Hackerfleet Community",
      author_email="packages@hackerfleet.org",
      url="https://github.com/hackerfleet/hfos",
      license="GNU General Public License v3",
      package_dir=packages,
      scripts=[
          'hfos.py',
      ],
      data_files=[
      ],

      long_description=include_readme(),
      dependency_links=['https://github.com/Hackerfleet/pynmea/archive/master.zip#egg=Pynmea-0.7.0',
                        'https://github.com/Hackerfleet/warmongo/archive/master.zip#egg=warmongo-0.5.3-hf'
      ],
      install_requires=['circuits==3.1.0',
                        'Pynmea==0.7.0',
                        'pymongo==3.0.1',
                        'warmongo==0.5.3-hf',
                        'jsonschema==2.4.0'
                        ],
      test_suite="tests.main.main"
)

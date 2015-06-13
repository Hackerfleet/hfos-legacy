#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Hackerfleet Technology Demonstrator License
# ===========================================
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

# TODO:
# Classifiers
# Keywords
# download_url
# platform

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
      data_files=[
      ],

      long_description="""HFOS - The Hackerfleet Operating System
=======================================

A modern, opensource approach to maritime navigation.

This software package is supposed to run on your ship/car/plane/ufo's board computer.
See https://github.com/hackerfleet/hfos""",
      dependency_links=[
          'https://github.com/Hackerfleet/pynmea/archive/master.zip#egg=pynmea-0.7.0',
          'https://github.com/Hackerfleet/warmongo/archive/master.zip#egg=warmongo-0.5.3.hf'
      ],
      install_requires=['circuits==3.1.0',
                        'pymongo==3.0.1',
                        'jsonschema==2.5.0',
                        'pynmea==0.7.0',
                        'warmongo==0.5.3.hf'
                        ],
      test_suite="tests.main.main",
      )

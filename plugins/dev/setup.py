#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System - Dev Plugin
# =================================================
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

from setuptools import setup, find_packages

setup(name="hfos-dev",
      version="0.0.1",
      description="hfos-dev",
      author="Hackerfleet Community",
      author_email="packages@hackerfleet.org",
      url="https://github.com/hackerfleet/hfos-dev",
      license="GNU General Public License v3",
      packages=find_packages(),
      scripts=[
          'hfos_manage.py'
      ],
      long_description="""HFOS - Dev
===========

HFOS module development system

This package is a useful starter point to set up new HFOS modules.
""",
      dependency_links=[],
      install_requires=[
          'hfos==1.1.0',
          'camelcase>=0.2.0',
          'pystache>=0.5.4'
      ],
      entry_points="""""",
      test_suite="tests.main.main",
      )

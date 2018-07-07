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
from hfos.tool.templates import insert_nginx_service

__author__ = "Heiko 'riot' Weinen"
__license__ = "AGPLv3"

from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop


def insert_service():
    definition = """# EtherCalc Module
    location /ethercalc/ {
        proxy_pass      http://127.0.0.1:8056/;
        include         proxy_params;
    }
    
    location /zappa/socket/__local/ {
        rewrite (.*) /ethercalc/$1;
    }
"""

    insert_nginx_service(definition)


class PostInstall(install):
    def run(self):
        install.run(self)
        insert_service()


class PostDevelop(develop):
    def run(self):
        develop.run(self)
        insert_service()


setup(name="hfos-calc",
      version="0.0.1",
      description="hfos-calc",
      author="Hackerfleet Community",
      author_email="riot@c-base.org",
      url="https://github.com/hackerfleet/hfos-calc",
      license="GNU Affero General Public License v3",
      packages=find_packages(),
      long_description="""HFOS - Calc
===========

A module to seamlessly integrate EtherCalc into HFOS.

This software package is a plugin module for HFOS.
""",
      dependency_links=[
      ],
      install_requires=[
          'hfos>=1.2.0',
      ],
      cmdclass={
          'develop': PostDevelop,
          'install': PostInstall
      },
      entry_points="""[hfos.components]
    spreadsheetwatcher=hfos.calc.spreadsheetwatcher:SpreadsheetWatcher
    [hfos.schemata]
    spreadsheet=hfos.calc.schemata.spreadsheet:Spreadsheet
    """,
      test_suite="tests.main.main",
      )

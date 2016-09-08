#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System - Library Plugin
# ====================================================
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

from setuptools import setup, find_packages

setup(name="hfos-library",
      version="0.0.1",
      description="hfos-library - a federated small library management system",
      author="Hackerfleet Community",
      author_email="packages@hackerfleet.org",
      url="https://github.com/hackerfleet/hfos-library",
      license="GNU General Public License v3",
      packages=find_packages(),
      long_description="""HFOS - Library
==============

A modern, opensource approach to library management.

This software package is a plugin module for HFOS.
""",
      dependency_links=['https://github.com/Hackerfleet/isbntools/archive/master.zip#egg=isbntools-4.3.1.hf'],
      install_requires=[
          'hfos==1.1.0',
          'isbntools==4.3.1.hf'
      ],
      entry_points="""[hfos.components]
    library=hfos.library.library:Library
[hfos.schemata]
    book=hfos.library.book:Book
    """,
      test_suite="tests.main.main",
      )

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System - Project Plugin
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

setup(name="hfos-project",
      version="0.0.1",
      description="hfos-project",

      author="Hackerfleet Community",
      author_email="packages@hackerfleet.org",
      url="https://github.com/hackerfleet/hfos-project",
      license="GNU General Public License v3",
      packages=find_packages(),
      long_description="""HFOS - Project
==============

A modern, opensource approach to project management.

This software package is a plugin module for HFOS.
""",
      dependency_links=[],
      install_requires=['hfos==1.1.0'],
      entry_points="""[hfos.schemata]
      project=hfos.project.project:Project
      task=hfos.project.task:Task
      [hfos.components]
      projectservice=hfos.project.projectservice:ProjectService
    """,
      test_suite="tests.main.main",
      )

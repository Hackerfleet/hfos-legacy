#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2017 Heiko 'riot' Weinen <riot@c-base.org> and others.
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

__author__ = "Heiko 'riot' Weinen"
__license__ = "GPLv3"

"""
Hackerfleet Operating System - Backend

Test HFOS Tools
===============



"""

# import os
import re
import pytest
from tempfile import NamedTemporaryFile
# from datetime import datetime
import dateutil.parser

from hfos import tools
from collections import namedtuple

template = """Hello {{placeholder}}!"""

content = {
    'placeholder': 'HFOS dev'
}


def test_uuid():
    uuid = tools.std_uuid()

    assert isinstance(uuid, str)
    assert re.match('(\w{8}(-\w{4}){3}-\w{12}?)', uuid)


def test_std_now():
    now = tools.std_now()

    assert isinstance(now, str)

    try:
        result = dateutil.parser.parse(now)
    except ValueError:
        pytest.fail('std_now produces nom parsable datetime strings')


def test_std_table():
    Row = namedtuple("Row", ['A', 'B'])
    rows = [
        Row("1", "2")
    ]

    table = tools.std_table(rows)

    rows.append(Row("345", "6"))
    table = tools.std_table(rows)


def test_format_template():
    result = tools.format_template(template, content)

    assert result == 'Hello HFOS dev!'


def test_format_template_file():
    with NamedTemporaryFile(prefix='hfos-test',
                            suffix='tpl',
                            delete=True) as f:
        f.write(template.encode('utf-8'))
        f.flush()
        result = tools.format_template_file(f.name, content)

    assert result == 'Hello HFOS dev!'


def test_write_template_file():
    with NamedTemporaryFile(prefix='hfos-test',
                            suffix='tpl',
                            delete=True) as f:
        f.write(template.encode('utf-8'))
        f.flush()

        target = f.name + '_filled'
        tools.write_template_file(f.name, target, content)

        with open(target, 'r') as tf:
            result = tf.readline()

        assert result == 'Hello HFOS dev!'

        print(target)

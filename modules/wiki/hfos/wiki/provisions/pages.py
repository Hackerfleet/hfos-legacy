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

"""

Provisioning: Wiki - Pages
==========================

Contains
--------

Wiki skeleton for ships


"""

WikiPages = [
    {
        'name': 'Index',
        'uuid': '8cc76c46-7488-4a0d-8ab9-1ca7c17f1b75',
        'title': 'Automatic Page Index',
        'html': 'No Index has been generated yet. This usually means, '
                'no pages exist.'
    }, {
        'name': 'Home',
        'uuid': '1c3a2ea5-64e3-4043-ad0a-fe0a01f6fa1e',
        'title': '#redirect Index',
        'html': 'There is no homepage by default, so this page redirects to '
                'the Index. To change that, just'
                '<a href="#!/editor/wikipage/1c3a2ea5-64e3-4043-ad0a'
                '-fe0a01f6fa1e/edit">edit this page and change the title</a>.'
    }
]


provision = {'data': WikiPages, 'model': 'wikipage'}



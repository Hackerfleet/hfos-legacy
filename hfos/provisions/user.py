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

Provisioning: User
==================

Contains
--------

Just creates a fulltext searchable index over the username field.


"""

from hfos.provisions.base import provisionList
from hfos.database import objectmodels
from hfos.logger import hfoslog, warn

from uuid import uuid4

Users = [{
    'name': 'System',
    'uuid': str(uuid4()),
    'roles': ['admin', 'system', 'crew']
}]


def provision(**kwargs):
    """Provision a system user"""

    # TODO: Add a root user and make sure owner can access it later.
    # Setting up details and asking for a password here is not very useful,
    # since this process is usually run automated.

    if kwargs.get('overwrite', False):
        hfoslog('Refusing to overwrite system user!', lvl=warn,
                emitter='PROVISIONS')
        kwargs['overwrite'] = False

    system_user_count = objectmodels['user'].count({'name': 'System'})
    if system_user_count == 0 or kwargs.get('clear', False):
        provisionList(Users, objectmodels['user'], **kwargs)
        hfoslog('Provisioning: Users: Done.', emitter="PROVISIONS")
    else:
        hfoslog('System user already present.', lvl=warn, emitter='PROVISIONS')


if __name__ == "__main__":
    provision()

"""


Module Schemata
===============

All JSONSchema compliant data schemata for HFOS

Contains
========

coords.py: Coordinates
mapview.py: Mapview objects
profile.py: User profile objects
user.py: User account objects

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

__license__ = """
Hackerfleet Technology Demonstrator
=====================================================================
Copyright (C) 2011-2014 riot <riot@hackerfleet.org> and others.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from hfos.schemata.client import Client
from hfos.schemata.user import User
from hfos.schemata.profile import Profile
from hfos.schemata.logmessage import LogMessage

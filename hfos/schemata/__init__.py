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

__all__ = [
    'client',
    'coords',
    'layer',
    'layergroup',
    'mapview',
    'profile',
    'controllable',
    'controller',
    'user',
    'wikipage',
    'vessel',
    'radio'
]

from importlib import import_module

from hfos.logger import hfoslog, verbose, debug, warn
from hfos.schemata.defaultform import defaultform


def _build_schemastore():
    result = {}

    for schemaname in __all__:
        hfoslog('[SCHEMATA] Adding Schema:', schemaname, lvl=verbose)
        schemamodule = import_module('hfos.schemata.' + schemaname)
        schema = None
        form = defaultform
        try:
            form = schemamodule.__form__
        except AttributeError:
            hfoslog("[SCHEMATA] No form found for schema %s, using defaultform." % schemaname, lvl=debug)

        try:
            schema = schemamodule.__schema__
        except AttributeError:
            hfoslog("[SCHEMATA] No schema found in schema %s!." % schemaname, lvl=warn)

        if schema and form:
            result[schemaname] = {'schema': schema, 'form': form}

    return result


schemastore = _build_schemastore()


def test():
    """Tests all included schemata against the Draft4Validator"""

    from jsonschema import Draft4Validator

    for schemaname, schemadata in schemastore.items():
        hfoslog("[SCHEMATA] Validating schema ", schemaname)
        Draft4Validator.check_schema(schemadata['schema'])
        if 'uuid' not in schemadata['schema']:
            hfoslog("[SCHEMATA] Schema without uuid encountered: ", schemaname, lvl=debug)

# https://github.com/fge/sample-json-schemas/tree/master/geojson

if __name__ == "__main__":
    test()

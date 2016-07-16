"""


Package: Provisions
===================

Initial client configuration data.
This contains tilelayer urls, api stuff etc.

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from importlib import import_module
from hfos.logger import hfoslog, verbose, error

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

__all__ = ['layers',
           'controllables',
           'controllers',
           'dashboards',
           'layers',
           'wiki'
           ]


def _build_provisionstore():
    result = {}

    for provisionname in __all__:
        hfoslog("Collecting Provision:", provisionname, lvl=verbose,
                emitter='PROVISIONS')

        try:
            provisionmodule = import_module('hfos.provisions.' + provisionname)
            provisionmethod = provisionmodule.provision
            result[provisionname] = provisionmethod
        except AttributeError:
            hfoslog("No provisioning method found for %s." % provisionname,
                    lvl=error, emitter='PROVISIONS')

    hfoslog("Found provisions: ", result.keys(), emitter='PROVISIONS')
    return result

# provisionstore = _build_provisionstore()

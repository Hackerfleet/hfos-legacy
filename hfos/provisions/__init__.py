"""


Package: Provisions
===================

Initial client configuration data.
This contains tilelayer urls, api stuff etc.

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from hfos.logger import hfoslog, debug  # , verbose, error, warn
from pkg_resources import iter_entry_points

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"


def _build_provisionstore():
    available = {}

    for provision_entrypoint in iter_entry_points(group='hfos.provisions',
                                                  name=None):
        hfoslog("Provisions found: ", provision_entrypoint.name, lvl=debug,
                emitter='DB')
        # try:
        available[provision_entrypoint.name] = provision_entrypoint.load()
        # except ImportError as e:
        #    hfoslog("Problematic provision: ", e, type(e),
        #            provision_entrypoint.name, exc=True, lvl=warn,
        #            emitter='PROVISIONS')

    hfoslog("Found provisions: ", available.keys(),
            emitter='PROVISIONS')
    # pprint(available)

    return available


provisionstore = _build_provisionstore()

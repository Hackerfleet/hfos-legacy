"""

Provisioning: Mapview
==================

Contains
--------

Mapview skeleton for ships

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.provisions.base import provisionList
from hfos.database import objectmodels
from hfos.logger import hfoslog

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

Mapviews = [
    {
        'name': 'Default OpenSeaMap + OpenStreetMap',
        'uuid': 'b69104cf-8ee7-4c81-aeca-dde272d67b63',
        'notes': 'Default empty mapview.',
        'layergroups': [
            '076b0b52-9ac8-4fdc-9e39-11141807e0e8',
            '22d57d5b-ceb2-47b3-9831-06290e6cbfe7'
        ]
    },
]


def provision():
    provisionList(Mapviews, objectmodels['mapview'], indexes=['name'],
                  clear=True)
    hfoslog('Provisioning: Mapviews: Done.', emitter='PROVISIONS')


if __name__ == "__main__":
    provision()

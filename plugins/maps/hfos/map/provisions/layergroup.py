"""

Provisioning: Layergroups
=========================

Contains
--------

Predefined groups of layers.

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from hfos.provisions.base import provisionList
from hfos.database import objectmodels
from hfos.logger import hfoslog

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

layergroups = [
    {
        "name": "Default",
        "uuid": "076b0b52-9ac8-4fdc-9e39-11141807e0e8",
        "shared": True,
        "notes": "Open Street Map and Open Sea Map, Satellite Overlay",
        "layers": [
            '2837298e-a3e8-4a2e-8df2-f475554d2f23',  # OSM
            '2bedb0d2-be9f-479c-9516-256cd5a0baae',  # OpenSeaMap
            '72611470-39b3-4982-8991-2ad467b06fc9'  # ESRI Satellite Shade Ovl
        ]
    }, {
        "name": "Satellite",
        "uuid": "889f580f-0aa4-46b6-96a1-87ef19030b0b",
        "shared": True,
        "notes": "ESRI Satellite and Open Sea Map",
        "layers": [
            '19e5704e-68a2-435e-9f21-ac389973cc7a',  # ESRI Satellite Shade
            '2bedb0d2-be9f-479c-9516-256cd5a0baae'  # OpenSeaMap

        ]
    }, {
        "name": "Weather",
        "uuid": "22d57d5b-ceb2-47b3-9831-06290e6cbfe7",
        "shared": True,
        "notes": "Open Street Map, Open Sea Map + OpenWeatherMaps",
        "layers": [
            '2837298e-a3e8-4a2e-8df2-f475554d2f23',  # OSM
            '2bedb0d2-be9f-479c-9516-256cd5a0baae',  # OpenSeaMap
            '7b73024e-9ede-4c90-821d-9c24c0cc0ff6',  # OWM Cloudlayer Ovl
        ]
    }
]


def provision():
    provisionList(layergroups, objectmodels['layergroup'], overwrite=True,
                  clear=True)
    hfoslog('Provisioning: Layergroups: Done.', emitter='PROVISIONS')


if __name__ == "__main__":
    provision()

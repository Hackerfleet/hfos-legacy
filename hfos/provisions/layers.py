"""

Provisioning: Layers
====================

Contains
--------

Predefined open layers.

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

from hfos.provisions.base import *
from hfos.database import layerobject

layers = [
    {
        "name": "OpenStreetMap",
        "description": "Open Street Map",
        "baselayer": True,
        "url": "http://localhost:8055/tilecache/a.tile.osm.org/{z}/{x}/{y}.png",
        "layerOptions": {
            "continuousWorld": False,
            "attribution": "&copy; <a href=\"http://osm.org/copyright\">OpenStreetMap</a> contributors"
        },
        "type": "xyz"
    },
    {
        "name": "OpenTopographyMap",
        "description": "Open Topography Map",
        "url": 'http://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        "layerOptions": {
            "maxZoom": 16,
            "attribution": '<a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy;\
<a href="https://opentopomap.org">OpenTopoMap</a>'
        }
    },
    {
        "name": "ESRI-Sat-Shaded",
        "description": "Shaded Satellite relief image data from ESRI",
        "baselayer": True,
        "url": 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}',
        "layerOptions": {
            "attribution": 'Tiles &copy; Esri &mdash; Source: Esri',
            "maxZoom": 13
        }
    },
    {
        "name": "OpenCycleMap",
        "baselayer": True,
        "description": "Open Cycle Map",
        "url": "http://localhost:8055/tilecache/a.tile.opencyclemap.org/cycle/{z}/{x}/{y}.png",
        "layerOptions": {
            "continuousWorld": True,
            "attribution": "&copy; <a href=\"http://www.opencyclemap.org/copyright\">OpenCycleMap</a> contributors"
        },
        "type": "xyz"
    },
    {
        "name": "OpenSeaMap",
        "description": "Open Sea Map",
        "baselayer": True,
        "url": "http://localhost:8055/tilecache/tiles.openseamap.org/seamark/{z}/{x}/{y}.png",
        "layerOptions": {
            "tms": True,
            "continuousWorld": True,
            "attribution": "&copy; OpenSeaMap contributors"
        },
        "type": "xyz"
    },
    {
        "name": "Hillshade-Europe",
        "description": "Hillshade layer for Europe from GIScience",
        "baselayer": False,
        "visible": False,
        "url": "http://localhost:8055/tilecache/129.206.228.72/cached/hillshade",
        "layerOptions": {
            "crs": {
                "code": "EPSG:900913",
                "Simple": {
                    "transformation": {
                        "_d": 0,
                        "_b": 0,
                        "_a": 1,
                        "_c": -1
                    },
                    "projection": {}
                },
                "transformation": {
                    "_d": 0.5,
                    "_b": 0.5,
                    "_a": 0.15915494309189535,
                    "_c": -0.15915494309189535
                },
                "projection": {
                    "MAX_LATITUDE": 85.0511287798
                }
            },
            "attribution": "Hillshade layer by GIScience http://www.osm-wms.de",
            "layers": "europe_wms:hs_srtm_europa",
            "format": "image/png",
            "opacity": 0.25
        },
        "type": "wms"
    },
    {
        "name": "ESRI-Sat-Shaded-Overlay",
        "description": "Shaded Satellite relief image data from ESRI as Overlay",
        "baselayer": False,
        "visible": False,
        "url": "http://localhost:8055/tilecache/server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "layerOptions": {
            "continuousWorld": True,
            "opacity": 0.25,
            "attribution": "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping,\
Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
        },
        "type": "xyz"
    },
    {
        "name": "OpenFireMap",
        "description": "Open Fire Map containing data about local fire safety",
        "baselayer": False,
        "visible": False,
        "url": "http://localhost:8055/tilecache/openfiremap.org/hytiles/{z}/{x}/{y}.png",
        "layerOptions": {
            "continuousWorld": True,
            "attribution": "&copy; <a href=\"http://www.openfiremap.org\">OpenFireMap</a> contributors"
        },
        "type": "xyz"
    },
    {
        "name": "OpenWeatherMap-Clouds",
        "description": "Open Weather Map showing clouds",
        "baselayer": False,
        "url": "http://localhost:8055/tilecache/a.tile.openweathermap.org/map/clouds/{z}/{x}/{y}.png",
        "layerOptions": {
            "continuousWorld": True,
            "attribution": "&copy; OpenWeatherMap"
        },
        "type": "xyz"
    }
]

if __name__ == "__main__":
    provisionList(layers, layerobject)
    hfoslog('Provisioning: Layers: Done.')

tilelayer = {
    "baselayers": {
        "osm": {
            "url": "http://localhost:8055/tilecache/a.tile.osm.org/{z}/{x}/{y}.png",
            "layerOptions": {
                "continuousWorld": False,
                "attribution": "&copy; <a href=\"http://osm.org/copyright\">OpenStreetMap</a> contributors"
            },
            "name": "OpenStreetMap",
            "type": "xyz"
        },
        "cycle": {
            "url": "http://localhost:8055/tilecache/a.tile.opencyclemap.org/cycle/{z}/{x}/{y}.png",
            "layerOptions": {
                "continuousWorld": True,
                "attribution": "&copy; <a href=\"http://www.opencyclemap.org/copyright\">OpenCycleMap</a> contributors - &copy; <a href=\"http://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors"
            },
            "name": "OpenCycleMap",
            "type": "xyz"
        },
        "openseamap": {
            "url": "http://localhost:8055/tilecache/tiles.openseamap.org/seamark/{z}/{x}/{y}.png",
            "layerOptions": {
                "tms": True,
                "continuousWorld": True,
                "attribution": "&copy; OpenSeaMap contributors"
            },
            "name": "OpenSeaMap",
            "type": "xyz"
        }
    },
    "overlays": {
        "hillshade": {
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
            "name": "Hillshade Europa",
            "type": "wms"
        },
        "esriimagery": {
            "visible": False,
            "url": "http://localhost:8055/tilecache/server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            "layerOptions": {
                "continuousWorld": True,
                "opacity": 0.25,
                "attribution": "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
            },
            "name": "Satellite ESRI World Imagery",
            "type": "xyz"
        },
        "openseamap": {
            "url": "http://localhost:8055/tilecache/t1.openseamap.org/seamark/{z}/{x}/{y}.png",
            "layerOptions": {
                "tms": True,
                "continuousWorld": False,
                "attribution": "&copy; OpenSeaMap contributors"
            },
            "name": "OpenSeaMap",
            "type": "xyz"
        },
        "fire": {
            "visible": False,
            "url": "http://localhost:8055/tilecache/openfiremap.org/hytiles/{z}/{x}/{y}.png",
            "layerOptions": {
                "continuousWorld": True,
                "attribution": "&copy; <a href=\"http://www.openfiremap.org\">OpenFireMap</a> contributors - &copy; <a href=\"http://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors"
            },
            "name": "OpenFireMap",
            "type": "xyz"
        },
        "openweathermap": {
            "url": "http://localhost:8055/tilecache/a.tile.openweathermap.org/map/clouds/{z}/{x}/{y}.png",
            "layerOptions": {
                "continuousWorld": True,
                "attribution": "&copy; OpenWeatherMap"
            },
            "name": "OpenWeatherMap Clouds",
            "type": "xyz"
        }
    }
}
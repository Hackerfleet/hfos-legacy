'use strict';

/* TODO
 * Structure this monster
 * Split up in parts
 * clean up all the lint
 * readd device detection support somewhere (elsewhere? use as service here?)
 */

import L from 'leaflet';
import Geo from 'mt-geo';
import LatLon from 'geodesy/latlon-vincenty';

import sidebar from './mapsidebar.tpl.html';

import leafletoverpasslayer from 'leaflet-overpass-layer';
import leafletdraw from 'leaflet-draw';
import leafletterminator from 'leaflet-terminator';
import leafletcoordinates from 'leaflet.coordinates/dist/Leaflet.Coordinates-0.1.5.min.js';
import leafletrotatedmarker from 'leaflet-rotatedmarker';
import leafleteasybutton from 'leaflet-easybutton';
import zoomslider from 'leaflet.zoomslider';
import contextmenu from 'leaflet-contextmenu';

import 'Leaflet.vector-markers/dist/leaflet-vector-markers.css';

let vectormarkers = require('Leaflet.vector-markers/dist/leaflet-vector-markers');
import default_marker from 'leaflet/dist/images/marker-icon.png';

// import 'Leaflet.Grid/L.Grid.css';
// import leafletgrid from 'Leaflet.Grid/L.Grid';

//import 'leaflet.simplegraticule/L.SimpleGraticule.css';
import 'leaflet.simplegraticule/L.SimpleGraticule.js';


import 'leaflet-easybutton/src/easy-button.css';
import 'leaflet.zoomslider/src/L.Control.Zoomslider.css';

import defaultIcon from '../assets/images/icons/default.png';
import vesselIcon from '../assets/images/icons/vessel.png';
import vesselMovingIcon from '../assets/images/icons/vessel-moving.png';
import vesselStoppedIcon from '../assets/images/icons/vessel-stopped.png';
import lighthouseIcon from '../assets/images/icons/lighthouse.png';


class mapcomponent {

    constructor(scope, leafletData, objectproxy, $state, $rootScope, socket, user, schemata, menu, notification, clipboard,
                navdata, $compile, $aside, uuid, NgTableParams) {
        this.scope = scope;
        this.leaflet = leafletData;
        this.op = objectproxy;
        this.state = $state;
        this.rootscope = $rootScope;
        this.socket = socket;
        this.user = user;
        this.schemata = schemata;
        this.menu = menu;
        this.notification = notification;
        this.clipboard = clipboard;
        this.navdata = navdata;
        this.uuid = uuid;

        this.mapviews = null;
        this.geoobjects = null;
        this.layergroups = {};
        this.other_layers = {};

        this.scope.otherCollapsed = true;

        this.baseLayer = null;

        this.layergroup = null;

        this.drawnLayer = new L.FeatureGroup();
        //this.drawnLayer.addLayer(new L.marker([50, 50]));
        this.objectlayers = {};

        this.vessel_display = 'off';

        this.default_color = 'red';
        this.default_marker = "poi";
        this.default_path = "route";
        this.default_shape = "danger";

        this.default_custom_marker = "Custom";
        this.default_custom_path = "Custom";
        this.default_custom_shape = "Custom";

        this.offline_loader = false;
        this.offline_loader_queue = {};
        this.offline_loader_zoom = 2;

        this.default_options = {
            marker: {
                poi: 'Point of interest',
                waypoint: 'Waypoint',
                custom: 'Custom'
            },
            path: {
                route: 'Route',
                vessel_trail: 'Vessel trail',
                custom: 'Custom'
            },
            shape: {
                danger: 'Dangerous zone',
                traffic: 'Traffic separation zone',
                industry: 'Industrial zone',
                fishing: 'Fishing zone',
                custom: 'Custom'
            }
        };

        this.map = '';

        let self = this;

        this.leafletlayers = {
            overlays: {},
            baselayers: {}
        };

        this.geojson = {};

        this.layer_flags = {};

        this.layers = {
            baselayers: {
                osm: {
                    name: 'OpenStreetMap',
                    type: 'xyz',
                    // url: 'http://{s}.tile.osm.org/{z}/{x}/{y}.png',
                    url: this.host + 'tilecache/a.tile.osm.org/{z}/{x}/{y}.png',
                    layerOptions: {
                        //subdomains: ['a', 'b', 'c'],
                        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
                        continuousWorld: false,
                        minZoom: 3
                    }
                }
            },
            overlays: {}
        };

        this.clearLayers = function () {
            self.layers.baselayers = {};
            self.layers.overlays = {};
            self.leafletlayers.baselayers = {};
            self.leafletlayers.overlays = {
                draw: {
                    name: 'draw',
                    type: 'group',
                    visible: true,
                    layerParams: {
                        showOnSelector: false
                    },
                    polyline: {
                        metric: false
                    }
                }
            };
        };

        this.clearLayers();

        this.host = 'http';
        if (socket.protocol === 'wss') {
            this.host = this.host + 's';
        }
        this.host = this.host + '://' + socket.host + ':' + socket.port + '/';

        this.follow = false;
        this.followlayers = false;

        this.mapviewuuid = null;

        this.deviceinfo = {}; // TODO: Fix this one. Needs angular device detector service

        this.center = {
            lat: 0,
            lng: 0,
            zoom: 4,
            autoDiscover: false
        };

        this.vessel = {
            coords: {
                lat: 54.17825,
                lng: 7.88888
            },
            course: 0,
            speed: 0,
            radiorange: 700
        };

        this.vessels = [];

        //L.VectorMarkers.Icon.prototype.options.prefix = 'fa';
        console.log("####################", vectormarkers);
        let DefaultMarker = vectormarkers.Icon;


        let Icons = {
            Default: L.icon({
                iconUrl: defaultIcon,
                //shadowUrl: 'leaf-shadow.png',

                iconSize: [25, 25], // size of the icon
                //shadowSize:   [50, 64], // size of the shadow
                iconAnchor: [12, 12], // point of the icon which will correspond to marker's location
                //shadowAnchor: [4, 62],  // the same for the shadow
                popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
            }),
            Vessel: L.icon({
                iconUrl: vesselIcon,
                //shadowUrl: 'leaf-shadow.png',

                iconSize: [25, 25], // size of the icon
                //shadowSize:   [50, 64], // size of the shadow
                iconAnchor: [12, 12], // point of the icon which will correspond to marker's location
                //shadowAnchor: [4, 62],  // the same for the shadow
                popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
            }),
            VesselMoving: L.icon({
                iconUrl: vesselMovingIcon,
                //shadowUrl: 'leaf-shadow.png',

                iconSize: [25, 25], // size of the icon
                //shadowSize:   [50, 64], // size of the shadow
                iconAnchor: [12, 12], // point of the icon which will correspond to marker's location
                //shadowAnchor: [4, 62],  // the same for the shadow
                popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
            }),
            VesselStopped: L.icon({
                iconUrl: vesselStoppedIcon,
                //shadowUrl: 'leaf-shadow.png',

                iconSize: [25, 25], // size of the icon
                //shadowSize:   [50, 64], // size of the shadow
                iconAnchor: [12, 12], // point of the icon which will correspond to marker's location
                //shadowAnchor: [4, 62],  // the same for the shadow
                popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
            }),
            Lighthouse: L.icon({
                iconUrl: lighthouseIcon,

                iconSize: [25, 25], // size of the icon
                //shadowSize:   [50, 64], // size of the shadow
                iconAnchor: [12, 12], // point of the icon which will correspond to marker's location
                //shadowAnchor: [4, 62],  // the same for the shadow
                popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
            })
        };

        this.controls = {
            draw: {
                draw: {
                    polyline: {
                        //metric: false
                    },
                    marker: {
                        icon: new DefaultMarker({
                            icon: 'flag',
                            iconColor: 'white',
                            markerColor: '#4384BF'
                        })
                    }
                },
                edit: {
                    featureGroup: new L.FeatureGroup()
                }
            },
            scale: {}
        };

        this.terminator = null;
        this.grid = null;

        this.tableParams = new NgTableParams({}, {
          getData: function (params) {
              // ajax request to api
              let filter;

              if (typeof filter === 'undefined') {
                  filter = {'owner': self.user.useruuid};
              }

              console.log("MAP_TABLE1:", params);
              let limit = params._params.count;
              let skip = limit * (params._params.page - 1);

              return self.op.search('geoobject', filter, '*', null, false, limit, skip).then(function(msg) {
                  let geoobjects = msg.data.list;
                  params.total(msg.data.size); // recal. page nav controls
                  console.log("MAP_TABLE2:", params);
                  self.geoobjects = geoobjects;
                  return geoobjects;
              });
          }
        });
        this.mapsidebar = $aside({scope: this.scope, template: sidebar, backdrop: false, show: false});

        this.showSidebar = function (event) {
            console.log('[MAP] Opening sidebar: ', self.mapsidebar);

            self.mapsidebar.$promise.then(function () {
                console.log("[MAP] Sidebar:", self.mapsidebar);
                self.mapsidebar.show();
            });
        };

        this.hasQueued = function () {
            return Object.keys(this.offline_loader_queue).length > 0
        };

        this.copyCoordinates = function (e) {
            console.log(e);
            self.clipboard.copyText(e.latlng);
        };

        this.centerMap = function (e) {
            self.map.panTo(e.latlng);
        };

        this.zoomTo = function (level) {
            self.map.setZoom(level);
        };

        this.zoomIn = function () {
            self.map.zoomIn();
        };

        this.zoomOut = function () {
            self.map.zoomOut();
        };

        this.openOSMiD = function (e) {
            let url = 'http://www.openstreetmap.org/edit?editor=id#map=', //52_17_28_N_5_32_32_E';
                lat = e.latlng.lat,
                lng = e.latlng.lng;

            url = url + self.map.getZoom() + '/' + lat.toString() + '/' + lng.toString();
            console.log(url);
            window.open(url, '_blank');
            window.focus();
        };

        this.openGeohack = function (e) {
            let url = 'https://tools.wmflabs.org/geohack/geohack.php?params=', //52_17_28_N_5_32_32_E';
                lat = e.latlng.lat,
                lng = e.latlng.lng;

            function getDegrees(angle) {
                let degrees = Math.floor(angle),
                    minutes = Math.floor(60 * (angle - degrees)),
                    seconds = Math.floor(3600 * (angle - degrees) - 60 * minutes);
                degrees = Math.abs(degrees);
                return degrees + "_" + minutes + "_" + seconds;
            }

            url = url + getDegrees(lat) + "_";
            if (lat > 0) {
                url = url + "N"
            } else {
                url = url + "S"
            }

            url = url + "_" + getDegrees(lng) + "_";
            if (lng > 0) {
                url = url + "E"
            } else {
                url = url + "W"
            }

            console.log(url);
            window.open(url, '_blank');
            window.focus();
        };

        this.defaults = {
            map: {
                contextmenu: true,
                contextmenuWidth: 140,
                contextmenuItems: [{
                    text: 'Copy coordinates',
                    callback: this.copyCoordinates
                }, {
                    text: 'Lookup on Geohack',
                    callback: this.openGeohack
                }, {
                    text: 'Edit map on OSM',
                    callback: this.openOSMiD
                }, {
                    text: 'Center map here',
                    callback: this.centerMap
                }, '-', {
                    text: 'Zoom in',
                    iconCls: 'fa fa-search-plus',
                    callback: this.zoomIn
                }, {
                    text: 'Zoom out',
                    iconCls: 'fa fa-search-minus',
                    callback: this.zoomOut
                }]
            }
        };

        this.events = {
            map: {
                enable: ['moveend', 'dblclick', 'mousemove'],
                logic: 'emit'
            }
        };

        this.editObject = function (uuid) {
            console.log('Editing layer:', uuid);
            let layer = this.objectlayers[uuid];
            this.drawnLayer.addLayer(layer);
        };

        this.addLayer = function (uuid) {
            console.log('[MAP] Getting Layer');
            self.op.get('layer', uuid).then(function (msg) {
                let layer = msg;
                console.log('[MAP] Got a layer:', layer);

                if (layer.type === 'geoobjects') {
                    self.getGeoobjects({'layer': uuid});
                } else {
                    layer.url = layer.url.replace('http://hfoshost/', self.host);
                }

                if (typeof layer.layerOptions.minZoom === 'undefined') {
                    layer.layerOptions.minZoom = 0;
                }
                if (typeof layer.layerOptions.maxZoom === 'undefined') {
                    layer.layerOptions.maxZoom = 18;
                }


                //let bounds = null;

                /*if (layer.layerOptions.bounds != null) {
                 let top_left = L.latLng(layer.layerOptions.bounds[0]),
                 top_right = L.latLng(layer.layerOptions.bounds[1]);
                 bounds = L.latLngBounds(top_left, top_right);
                 //layer.layerOptions.bounds = bounds;
                 //delete layer.layerOptions['bounds'];
                 }*/

                console.log('[MAP] Adding layer:', layer);
                if (layer.baselayer === true) {
                    self.layers.baselayers[layer.uuid] = layer;
                    if (_.isEmpty(self.leafletlayers.baselayers)) {
                        self.switchLayer('baselayers', layer.uuid);
                    }
                } else {
                    self.layers.overlays[layer.uuid] = layer;
                }
                self.layer_flags[layer.uuid] = {
                    expanded: false,
                    zoom: [layer.layerOptions.minZoom, layer.layerOptions.maxZoom]
                }
            })
        };

        this.removeLayer = function (uuid) {
            let layer = self.op.objects[uuid];
            console.log('[MAP] Removing layer:', layer);
            if (layer.baselayer === true) {
                self.layers.baselayers.delete(uuid);
            } else {
                self.layers.overlays.delete(uuid);
            }
            self.layer_flags.delete(uuid);
        };

        this.toggleLayer = function (state, uuid) {
            console.log('[MAP] Oh, you selected layer:', state, uuid);
            if (state === true) {
                self.addLayer(uuid);
            } else {
                self.removeLayer(uuid);
            }
        };

        this.switchLayer = function (type, uuid) {
            console.log('[MAP] Current Layers:', self.layers);
            if (type == 'baselayers') {
                console.log('[MAP] Switching base layer: ', uuid);
                this.baseLayer = uuid;
                this.leafletlayers.baselayers = {};
                this.leafletlayers.baselayers[uuid] = this.layers.baselayers[uuid];
            } else {
                console.log('[MAP] Switching overlay: ', uuid);
                let overlays = this.leafletlayers.overlays;
                if (overlays.hasOwnProperty(uuid)) {
                    delete overlays[uuid];
                } else {
                    let layer;
                    if (this.layers.overlays.hasOwnProperty(uuid)) {
                        layer = this.layers.overlays[uuid];
                    } else if (this.other_layers.hasOwnProperty(uuid)) {
                        layer = this.other_layers[uuid];
                    }

                    layer.visible = true;
                    console.log('[MAP] New overlay:', layer);
                    overlays[uuid] = layer;
                }
            }
            console.log('[MAP] LAYERS:', self.leafletlayers);
        };


        this.switchLayergroup = function (uuid) {
            console.log('[MAP] Switching to new layergroup: ', uuid);
            self.op.getObject('layergroup', uuid);
            self.layergroup = uuid;
            self.clearLayers();
        };

        this.switchMapview = function (uuid) {
            console.log('[MAP] Switching to new mapview: ', uuid);
            self.mapviewuuid = uuid;
            self.layergroup = false;
            self.op.getObject('mapview', uuid);
        };

        this.switchGeoobject = function (uuid) {
            this.op.getObject('geoobject', uuid)
        };

        this.zoom_to_geoobject = function (uuid) {
            console.log('[MAP] Zooming to geoobject');
            let coords = this.geoobjects[uuid].geojson.geometry.coordinates,
                target = [coords[1], coords[0]];
            this.map.setView(target, 15, {animate: true});
        };

        this.getLayergroups = function () {
            console.log('[MAP] Checking layergroups:', self.mapview);
            if (typeof self.mapview.layergroups !== 'undefined') {
                self.layergroup = self.mapview.layergroups[0];
                for (let group of self.mapview.layergroups) {
                    self.op.getObject('layergroup', group);
                }
            }
        };

        this.show_map_boundary = function (uuid) {
            console.log('[MAP] Zooming to chart extents');
            if (!this.leafletlayers.overlays.hasOwnProperty(uuid)) {
                this.switchLayer('overlays', uuid);
            }
            this.map.fitBounds(this.layers.overlays[uuid].layerOptions.bounds);
        };

        this.get_offline_data = function () {
            console.log('[MAP] Requesting extent for offline use');
            let bounds = self.map.getBounds();
            console.log('[MAP] bounds:', bounds);
            let rect = [
                bounds._southWest.lng, bounds._southWest.lat,
                bounds._northEast.lng, bounds._northEast.lat
            ];
            let layers = [];
            let uuid = null;

            for (uuid in self.leafletlayers.baselayers) {
                if (self.layers.baselayers.hasOwnProperty(uuid)) {
                    layers.push(uuid);
                }
            }
            for (uuid in self.leafletlayers.overlays) {
                if (self.layers.overlays.hasOwnProperty(uuid)) {
                    layers.push(uuid);
                }
            }
            let event = {
                'component': 'hfos.map.maptileservice',
                'action': 'request_maptile_area',
                'data': {
                    'extent': rect,
                    'zoom': self.center.zoom + self.offline_loader_zoom,
                    'layers': layers
                }
            };
            self.socket.send(event);
        };

        this.queue_trigger = function (uuid) {
            console.log('[MAP] Requesting download of queue', uuid);
            let event = {
                'component': 'hfos.map.maptileservice',
                'action': 'queue_trigger',
                'data': uuid
            };
            self.socket.send(event);
        };
        this.queue_cancel = function () {
            console.log('[MAP] Requesting cancellation of queues', uuid);
            let event = {
                'component': 'hfos.map.maptileservice',
                'action': 'queue_cancel'
            };
            self.socket.send(event);
        };
        this.queue_remove = function (uuid) {
            console.log('[MAP] Requesting removal of queue', uuid);
            let event = {
                'component': 'hfos.map.maptileservice',
                'action': 'queue_remove',
                'data': uuid
            };
            self.socket.send(event);
        };


        function handle_maptileservice(msg) {
            if (msg.action === 'queued') {
                console.log('[MAP] Loader request was queued');
                self.offline_loader_queue[msg.data.uuid] = msg.data;
            } else if (msg.action === 'empty') {
                console.log('[MAP] No tiles to fetch');
                self.notification.add('warning', 'No tiles to fetch', 'The area you selected does not contain any tile data.')
            } else if (msg.action === 'acting') {
                self.offline_loader_queue[msg.data].acting = true;
                self.notification.add('success', 'Caching tiles', 'The system tries to download the requested tiles now.')
            } else if (msg.action === 'offline_loader_progress') {
                self.offline_loader_queue[msg.data.queue].completed = msg.data.completed;
            } else if (msg.action === 'removed') {
                delete self.offline_loader_queue[msg.data.uuid];
            }
        }

        this.socket.listen('hfos.map.maptileservice', handle_maptileservice);

        this.toggle_vessels = function (state) {
            this.vessel_display = state;
        };

        this.scope.$on('OP.Get', function (event, objuuid, obj, schema) {
            console.log('[MAP] Object:', obj, schema);
            if (objuuid === self.mapviewuuid) {
                self.updateMapview(objuuid);
                self.clearLayers();
            } else if (schema === 'geoobject') {
                console.log('[MAP] Geoobject received: ', obj);
                self.geoobjects[obj.uuid] = obj;
                let map_object;

                if (obj.geojson.geometry.type === 'Point') {
                    let marker_icon = new DefaultMarker({
                        icon: obj.icon,
                        iconColor: obj.iconcolor,
                        markerColor: obj.color
                    });
                    let pos = obj.geojson.geometry.coordinates;
                    map_object = L.marker([pos[1], pos[0]], {icon: marker_icon}).addTo(self.map);
                    self.addContextMenu(map_object, obj.uuid);
                } else {
                    map_object = L.geoJson(obj.geojson, {color: obj.color});
                    console.log('Map Object:', map_object);
                    self.addContextMenu(map_object, obj.uuid);

                    map_object.addTo(self.map);
                    self.drawnLayer.addLayer(map_object);
                }

                console.log('DRAWN LAYERS:', self.drawnLayer);
                self.objectlayers[obj.uuid] = map_object;
            } else if (schema === 'layergroup') {
                console.log('[MAP] Layergroup received:', obj);
                if (self.layergroup == obj.uuid) {
                    console.log('[MAP] Activating layergroup ', obj.uuid);
                    self.clearLayers();

                    if (typeof obj.layers !== 'undefined') {
                        for (let layer of obj.layers) {
                            self.op.getObject('layer', layer);
                        }
                    }
                } else {
                    console.log('[MAP] Not active, storing');
                    self.layergroups[obj.uuid] = obj;
                }

            } else if (schema === 'layer') {
                console.log('[MAP] Received layer object: ', obj);

                if (self.layergroups[self.layergroup].layers.indexOf(objuuid) >= 0) {
                    console.log('[MAP] Is activated layer');
                    self.addLayer(objuuid);
                    console.log('[MAP] Layer flags after adding:', self.layer_flags);
                } else {
                    console.log('[MAP] Inactive layer');
                }
            }
        });

        this.scope.$on('OP.ListUpdate', function (event, schema) {
            /*if (schema === 'geoobject') {
                let list = self.op.lists.geoobject;

                console.log('[MAP] Map received a list of geoobjects: ', schema, list);
                self.geoobjects = list;
                self.geoobject_tableParams = new NgTableParams(
                    {},
                    {
                        dataset: self.geoobjects
                    }
                );


                /*for (let item of list) {
                 console.log('[MAP] Item:', item);
                 console.log('[MAP] Layer:', self.drawnLayer);


                 let myLayer = L.geoJson().addTo(self.map);
                 console.log('[MAP] This strange thing:', myLayer);
                 myLayer.addData(item.geojson);

                 //self.drawnLayer.addData(item.geojson);
                 }
            }*/
            if (schema === 'layergroup') {
                self.layergroups = self.op.lists.layergroup;
            }
            if (schema === 'mapview') {
                self.mapviews = self.op.lists.mapview;
            }
        });

        this.scope.$on('OP.Update', function (event, objuuid) {
            if (objuuid === self.mapviewuuid) {
                self.updateMapview(objuuid);
                self.syncFromMapview();
            }
        });

        this.syncToMapview = function () {
            console.log('[MAP] MAPVIEWUUID: ', self.mapviewuuid);
            if (self.mapviewuuid !== null) {
                self.mapview.coords = self.center;
                console.log('[MAP] Sync to MV: ', self.mapview);
                if (self.sync) {
                    self.op.putObject('mapview', self.mapview);
                }
            }
        };

        this.updateMapview = function (objuuid) {
            if (objuuid === self.mapviewuuid) {
                console.log('[MAP] Received associated mapview.');
                self.mapview = self.op.objects[objuuid];
                //if (self.followlayers === true || self.layergroup == false) {
                self.getLayergroups();
                //}
            }
        };

        this.syncFromMapview = function () {
            if (self.mapviewuuid !== null) {
                self.center = self.mapview.coords;
                self.scope.$apply();
                console.log('[MAP] Sync from MV: ', self.center);
            }
        };

        this.getGeoobjects = function (filter) {
            /*console.log('[MAP] Getting geoobjects');
            if (typeof filter === 'undefined') {
                filter = {'owner': self.user.useruuid};
            }
            self.op.getList('geoobject', filter);
            */
        };

        this.getMapview = function () {
            console.log('[MAP] Getting associated mapview.');

            self.mapviewuuid = self.user.clientconfig.mapviewuuid;

            console.log('[MAP] Clientconfig Mapview UUID: ', self.mapviewuuid);

            if (self.mapviewuuid === '' || typeof self.mapviewuuid === 'undefined') {
                console.log('[MAP] Picking user profile mapview', self.user.profile);
                self.mapviewuuid = self.user.profile.settings.mapviewuuid;
            }
            console.log('[MAP] Final Mapview UUID: ', self.mapviewuuid);

            if (self.mapviewuuid !== null && typeof self.mapviewuuid !== 'undefined' && self.mapviewuuid !== '') {
                self.op.getObject('mapview', self.mapviewuuid);
            } else {
                self.mapviewuuid = null; // Normalize unset mapview
            }
        };

        this.get_other_layers = function () {
            this.op.search('layer', '', '*').then(function (msg) {
                let other_layers = msg.data.list;
                console.log('[MAP] Got a list of all layers');
                for (let item of other_layers) {
                    // TODO: Kick out layers that are already in mapview?
                    self.other_layers[item.uuid] = item;
                }
            })
        };

        this.getMapdataLists = function () {
            console.log('[MAP] Getting available map data objects.');
            self.op.getList('layergroup');
            self.op.getList('mapview', {}, ['name', 'uuid', 'viewtype']);
        };

        this.requestMapData = function () {
            console.log('[MAP] Requesting mapdata from server.');

            self.getMapview();
            self.getGeoobjects();
            self.getMapdataLists();
        };

        this.subscribe = function () {
            self.op.subscribeObject(self.mapviewuuid, 'mapview');
        };

        this.unsubscribe = function () {
            self.op.unsubscribeObject(self.mapviewuuid, 'mapview');
        };

        let mapEvents = self.events.map.enable;

        let handleEvent = function (event) {
            if (self.user.signedin === true) {
                //console.log('[MAP] Map Event:', event);
                if (event.name === 'leafletDirectiveMap.moveend') {
                    if (self.sync) {
                        console.log('[MAP] Synchronizing map');
                        self.syncToMapview();
                    }
                    if (self.vessel_display !== 'off') {
                        let bounds = self.map.getBounds();
                        console.log('bounds:', bounds);
                        let rect = [
                            [bounds._northEast.lng, bounds._northEast.lat],
                            [bounds._southWest.lng, bounds._southWest.lat]
                        ];
                        let filter = {
                            'geojson': {
                                '$geoWithin': {
                                    '$box': rect
                                }
                            }
                        };
                        console.log('[MAP] Vesselfilter:', filter);
                        self.op.search('vessel', filter, '*').then(function (msg) {
                            console.log('[MAP] Returned Vessel data:', msg);
                            self.vessels = msg.data.list;
                            self.map.UpdateVessels();
                        });
                    }
                } else if (event.name === 'leafletDirectiveMap.dblclick') {
                    //console.log(self.layers);
                } else if (event.name === 'leafletDirectiveMap.mousemove') {
                    //console.log(event);
                }
            }
            if (event.name === 'leafletDirectiveMap.mousemove') {
                $('#statusCenter').text(event.latlng);
            }
        };

        for (let k of mapEvents) {
            let eventName = 'leafletDirectiveMap.' + k;
            this.scope.$on(eventName, function (event) {
                handleEvent(event);
            });
        }

        leafletData.getMap().then(function (map) {
            console.log('[MAP] Setting up initial map settings.');
            self.map = map;

            map.on('click', function (e) {
                $('#statusCenter').html = 'Latitude: ' + e.latlng.lat + ' Longitude: ' + e.latlng.lng;
            });

            map.setZoom(2);
            //map.panTo({lat: 52.513, lon: 13.41998});

            //if (self.deviceinfo.type !== 'mobile') {
            //    let Zoomslider = new L.Control.Zoomslider().addTo(map);
            //    $('.leaflet-control-zoom').css('visibility', 'hidden');
            //}

            self.terminator = leafletterminator()
                .setStyle({
                    weight: 1,
                    color: '#000',
                    fill: '#000'
                });
            self.terminator.addTo(map);

            /*
             L.simpleGraticule({
             interval: 20,
             showOriginLabel: true,
             redraw: 'move',
             zoomIntervals: [
             {start: 0, end: 3, interval: 50},
             {start: 4, end: 5, interval: 5},
             {start: 6, end: 20, interval: 1}
             ]
             }).addTo(map);
             */
            //self.grid = L.grid({redraw: 'moveend'}).addTo(map);

            //let PanControl = L.control.pan().addTo(map);
            self.courseplot = L.polyline([], {color: 'red'}).addTo(map);

            //map.addLayer(self.drawnLayer);

            self.zoom_to_vessel = L.easyButton({
                id: 'btn_zoom_to_vessel',
                states: [{
                    stateName: 'default',
                    icon: 'fa-crosshairs',
                    onClick: function (control) {
                        let target = self.vessel.coords;
                        self.map.setView(target, 15, {animate: true});
                    }
                }],
                title: 'Toggle editing of GeoObjects'
            });

            self.toggledraw = L.easyButton({
                id: 'btn_toggledraw',
                states: [{
                    stateName: 'disabled',
                    icon: 'fa-pencil',
                    onClick: function (control) {
                        self.drawing = true;
                        $('.leaflet-draw').show();
                        control.state('enabled');
                    }
                }, {
                    stateName: 'enabled',
                    icon: 'fa-pencil',
                    onClick: function (control) {
                        self.drawing = false;
                        $('.leaflet-draw').hide();
                        control.state('disabled');
                    }
                }],
                title: 'Toggle editing of GeoObjects'
            });

            self.togglefollow = L.easyButton({
                id: 'btn_togglefollow',
                states: [{
                    stateName: 'static',
                    icon: 'fa-eye-slash',
                    onClick: function (control) {
                        if (self.mapviewuuid === null) {
                            self.notification.add('warning', 'No mapview', 'There is no mapview selected that you could follow. Use the menu to select one.');
                            return;
                        }
                        self.follow = true;
                        self.followlayers = true;
                        self.subscribe();
                        control.state('following');
                    }
                }, {
                    stateName: 'following',
                    icon: 'fa-eye',
                    onClick: function (control) {
                        self.followlayers = false;
                        control.state('followinglimited');
                    }
                }, {
                    stateName: 'followinglimited',
                    icon: 'fa-low-vision',
                    onClick: function (control) {
                        self.follow = false;
                        self.unsubscribe();
                        control.state('static');
                    }
                }],
                title: 'Toggle map following'
            });

            self.togglesync = L.easyButton({
                id: 'btn_togglesync',
                states: [{
                    stateName: 'unsynchronized',
                    icon: 'fa-chain-broken',
                    onClick: function (control) {
                        if (self.mapviewuuid === null) {
                            self.notification.add('warning', 'No mapview', 'There is no mapview selected that you could follow. Use the menu to select one.');
                            return;
                        }
                        console.log('[MAP] Enabling synchronization');
                        self.sync = true;
                        control.state('synchronized');
                    }
                }, {
                    stateName: 'synchronized',
                    icon: 'fa-chain',
                    onClick: function (control) {
                        console.log('[MAP] Disabling synchronization');
                        self.sync = false;
                        control.state('unsynchronized');
                    }
                }],
                title: 'Toggle synchronization to ship'
            });

            self.toggledash = L.easyButton({
                id: 'btn_toggledash',
                states: [{
                    stateName: 'nodash',
                    icon: 'fa-tachometer',
                    onClick: function (control) {
                        console.log('[MAP] Enabling Dashboard');
                        self.dashboardoverlay = true;
                        $('#btn_toggledash').css({'color': '#000'});
                        control.state('dash');
                    }
                }, {
                    stateName: 'dash',
                    icon: 'fa-tachometer',
                    onClick: function (control) {
                        console.log('[MAP] Disabling Dashboard');
                        self.dashboardoverlay = false;
                        $('#btn_toggledash').css({'color': '#aaa'});
                        control.state('nodash');
                    }
                }],
                title: 'Toggle dashboard overlay'
            });

            self.togglevesseldisplay = L.easyButton({
                id: 'btn_togglevesseldisplay',
                states: [{
                    stateName: 'low',
                    icon: 'fa-paper-plane-o',
                    onClick: function (control) {
                        console.log('[MAP] Toggling vessel display (high detail)');
                        control.state('high');
                        self.toggle_vessels('high');
                        update_show_vessels();
                    }
                }, {
                    stateName: 'high',
                    icon: 'fa-paper-plane',
                    onClick: function (control) {
                        console.log('[MAP] Disabling vessel display');
                        $('#btn_togglevesseldisplay').css({'color': '#aaa'});
                        control.state('off');
                        self.toggle_vessels('off');
                    }
                }, {
                    stateName: 'off',
                    icon: 'fa-paper-plane-o',
                    onClick: function (control) {
                        console.log('[MAP] Enabling vessel display (low detail)');
                        $('#btn_togglevesseldisplay').css({'color': '#000'});
                        control.state('low');
                        self.toggle_vessels('low');
                        update_show_vessels();
                    }
                }],
                title: 'Toggle display of other nearby vessels'
            });

            self.toggleradiorange = L.easyButton({
                id: 'btn_toggleradiorange',
                states: [{
                    stateName: 'off',
                    icon: 'fa-wifi',
                    onClick: function (control) {
                        console.log('[MAP] Enabling radio range display');
                        $('#btn_toggleradiorange').css({'color': '#aaa'});
                        control.state('on');
                    }
                }, {
                    stateName: 'on',
                    icon: 'fa-wifi',
                    onClick: function (control) {
                        console.log('[MAP] Disabling radio range display');
                        $('#btn_toggleradiorange').css({'color': '#000'});
                        control.state('off');
                    }
                }],
                title: 'Toggle radio range display of nearby vessels'
            });

            self.toggleterminator = L.easyButton({
                id: 'btn_toggleterminator',
                states: [{
                    stateName: 'off',
                    icon: 'fa-sun-o',
                    onClick: function (control) {
                        console.log('[MAP] Disabling terminator display');
                        $('#btn_toggleterminator').css({'color': '#aaa'});
                        control.state('on');
                        map.removeLayer(self.terminator);
                    }
                }, {
                    stateName: 'on',
                    icon: 'fa-sun-o',
                    onClick: function (control) {
                        console.log('[MAP] Enabling terminator display');
                        $('#btn_toggleterminator').css({'color': '#000'});
                        control.state('off');
                        self.terminator.addTo(map);
                    }
                }],
                title: 'Toggle display of terminator'
            });

            self.zoom_to_vessel.addTo(map);
            self.toggledraw.addTo(map);
            self.togglefollow.addTo(map);
            self.togglesync.addTo(map);
            self.toggledash.addTo(map);
            self.togglevesseldisplay.addTo(map);
            self.toggleradiorange.addTo(map);
            self.toggleterminator.addTo(map);


            self.addContextMenu = function (layer, uuid) {
                console.log('[MAP] Adding context menu to geoobject');
                layer.on('click', function (e) {
                    self.editObject(uuid);
                    // TODO: This is not angular-compatible - no access to this or other controllers
                    L.popup().setContent('<h2>Marker</h2>' +
                        '<div><a href="#!/editor/geoobject/' + uuid + '/edit">Edit Object in Editor</a></div>')
                        .setLatLng(e.latlng)
                        .openOn(map);
                });
            };

            leafletData.getLayers().then(function (baselayers) {
                let drawnItems = baselayers.overlays.draw;
                self.drawnLayer = drawnItems;
                console.log('[MAP] The basedrawlayer looks like this:', drawnItems);
                map.on('draw:created', function (e) {
                    let layer = e.layer;
                    let uuid = self.uuid.v4();
                    console.log('[MAP] Map drawing created:', e, ' layer:', layer);
                    self.addContextMenu(layer, uuid);
                    drawnItems.addLayer(layer);

                    let geojson = layer.toGeoJSON();

                    console.log(geojson);

                    self.geojson = geojson;

                    let objtype = "UNSET";
                    if (geojson.geometry.type === 'Point') {
                        objtype = self.default_marker;
                        if (objtype === 'Custom') {
                            objtype = self.default_custom_marker;
                        }
                    } else if (geojson.geometry.type === 'LineString') {
                        objtype = self.default_path;
                        if (objtype === 'Custom') {
                            objtype = self.default_custom_path;
                        }
                    } else if (geojson.geometry.type === 'Polygon') {
                        objtype = self.default_shape;
                        if (objtype === 'Custom') {
                            objtype = self.default_custom_shape;
                        }
                    }


                    let geoobject = {
                        uuid: uuid,
                        //owner: self.user.useruuid,
                        geojson: geojson,
                        type: objtype,
                        color: self.default_color
                    };
                    self.op.putObject('geoobject', geoobject);
                });
            });

            $('.leaflet-draw').hide();

            L.RotatedMarker = L.Marker.extend({
                options: {angle: 0},
                _setPos: function (pos) {
                    L.Marker.prototype._setPos.call(this, pos);
                    if (L.DomUtil.TRANSFORM) {
                        // use the CSS transform rule if available
                        this._icon.style[L.DomUtil.TRANSFORM] += ' rotate(' + this.options.angle + 'deg)';
                    } else if (L.Browser.ie) {
                        // fallback for IE6, IE7, IE8
                        let rad = this.options.angle * L.LatLng.DEG_TO_RAD,
                            costheta = Math.cos(rad),
                            sintheta = Math.sin(rad);
                        this._icon.style.filter += ' progid:DXImageTransform.Microsoft.Matrix(sizingMethod=\'auto expand\', M11=' +
                            costheta + ', M12=' + (-sintheta) + ', M21=' + sintheta + ', M22=' + costheta + ')';
                    }
                }
            });

            L.rotatedMarker = function (pos, options) {
                return new L.RotatedMarker(pos, options);
            };


            let VesselMarker = L.rotatedMarker(self.vessel.coords, {icon: Icons.Vessel}).addTo(map);

            function update_show_vessels() {
                console.log('[MAP] Toggling Show Vessels');

                if (self.togglevesseldisplay.state === 'off') {
                    for (let vessel of self.vessels) {
                        if (vessel.marker !== false) {
                            map.removeLayer(vessel.marker);
                        }
                        if (vessel.plot !== false) self.map.removeLayer(vessel.plot);
                        vessel.marker = vessel.plot = false;
                    }
                } else {
                    map.UpdateVessels();
                }
            }

            function update_show_radiorange() {
                console.log('[MAP] Toggling Show Radiorange');

                if (self.toggleradiorange.state === 'off') {
                    for (let vessel of self.vessels) {

                        if (vessel.rangedisplay !== false) {
                            self.map.removeLayer(vessel.rangedisplay);
                            vessel.rangedisplay = false;
                        }
                    }
                    self.map.removeLayer(self.RangeDisplay);
                    self.RangeDisplay = false;
                } else {
                    map.UpdateVessels();
                }
            }

            map.UpdateVessels = function () {
                console.log('UpdateVessels called');
                console.log('Icons:', Icons);
                if (self.vessel_display !== 'off') {
                    console.log('[MAP] Updating vessels:', self.vessels);
                    for (let vessel of self.vessels) {
                        let icon = Icons.Default;

                        console.log('[MAP] OSDMVESSELDISPLAY: ', vessel);

                        if (self.toggleradiorange.state === 'on') {
                            if (vessel.rangedisplay === false) {
                                let circle = L.circle(vessel.coords, vessel.radiorange, {
                                    color: '#6494BF',
                                    fillColor: '#4385BF',
                                    fillOpacity: 0.4
                                }).addTo(map);
                                vessel.range_risplay = circle;
                            }
                        }

                        if (vessel.sog > 0) {
                            console.log('[MAP] Is moving:', vessel.sog, vessel.cog);

                            let dist = (vessel.sog * 1852) * (5 / 60);

                            /* let target = [0,0];
                             target[0] = Math.asin( Math.sin(coords[0])*Math.cos(d/R) + Math.cos(coords[0])*Math.sin(d/R)*Math.cos(course) );
                             target[1] = coords[1] + Math.atan2(Math.sin(course)*Math.sin(d/R)*Math.cos(coords[0]), Math.cos(d/R)-Math.sin(coords[0])*Math.sin(target
                             */

                            let lat1 = Geo.parseDMS(vessel.geojson.coordinates[0]);
                            let lon1 = Geo.parseDMS(vessel.geojson.coordinates[1]);
                            let cog = vessel.cog;

                            // calculate destination point, final bearing
                            let p1 = LatLon(lat1, lon1);
                            console.log(p1);
                            console.log(LatLon);
                            let p2 = p1.destinationPoint(dist, cog);
                            let brngFinal = p1.finalBearingTo(p2);

                            //console.log('[MAP] OSDMVESSELDISPLAY-ARROW: Distance travelled in 5 min:', dist, 'Coords: ', p1, ' Coords in 5 min:', p2, ' Final Bearing:',
                            if (typeof vessel.plot === 'undefined') {
                                vessel.plot = L.polyline([p1, p2], {color: 'red'}).addTo(map);
                            } else {
                                vessel.plot.setLatLngs([p1, p2]);
                            }

                            icon = Icons.VesselMoving;

                        } else {
                            console.log('[MAP] Is stopped');
                            if (typeof vessel.plot !== 'undefined') {
                                map.removeLayer(vessel.plot);
                                delete vessel.plot;
                            }
                            icon = Icons.VesselStopped;
                        }

                        console.log('[MAP] Icon:', icon);


                        if (typeof vessel.marker !== 'undefined') {
                            vessel.marker.setLatLng(vessel.geojson.coordinates);
                            vessel.marker.options.angle = vessel.cog;
                            vessel.marker.update();
                        } else {
                            vessel.marker = L.rotatedMarker(vessel.geojson.coordinates, {icon: icon}).addTo(map);
                            vessel.marker.options.angle = vessel.cog;
                            vessel.marker.update();
                        }
                    }
                }
            };


            function UpdateMapMarker() {
                console.log('[MAP] Getting current Vessel position');

                Coords = response.coords;
                Course = response.course;
                console.log('[MAP] Coords: ' + Coords + ' Course:' + Course);

                courseplot.addLatLng(Coords);
                plotted = courseplot.getLatLngs();

                if (plotted.length > 50) {
                    courseplot.spliceLatLngs(0, 1);
                }

                VesselMarker.setLatLng(Coords);
                VesselMarker.options.angle = Course;
                VesselMarker.update();

                if ($('#cb_show_radiorange').is(':checked')) {
                    if (RangeDisplay == false) {
                        let circle = L.circle(Coords, Radiorange, {
                            color: '#67BF64',
                            fillColor: '#67BF64',
                            fillOpacity: 0.4
                        }).addTo(map);
                        RangeDisplay = circle;
                    }
                }
            }
        });

        this.scope.$on('Profile.Update', function () {
            console.log('[MAP] Profile update - fetching map data');
            self.requestMapData();
        });
        if (this.user.signedin === true) {
            console.log('[MAP] Logged in - fetching map data');
            this.requestMapData();
        }

        this.scope.$on('$destroy', function () {
            console.log('[MAP] Destroying controller');
            console.log(self.mapsidebar);
            self.mapsidebar.hide();
        })
    }

    gdal_upload() {
        console.log('Uploading new map file.');

        let file = document.getElementById('filename').files[0];
        console.log('file: ', file);
        this.socket.sendFile(file, 'hfos.map.gdal', 'mapimport');

    }

    gdal_rescan() {
        console.log('Triggering rastertile path rescan.');

        this.socket.send({
            component: 'hfos.map.gdal',
            action: 'rescan'
        });

    }
}

mapcomponent.$inject = ['$scope', 'leafletData', 'objectproxy', '$state', '$rootScope', 'socket', 'user', 'schemata',
    'menu', 'notification', 'clipboard', 'navdata', '$compile', '$aside', 'uuid', 'NgTableParams'];

export default mapcomponent;

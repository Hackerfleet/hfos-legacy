'use strict';

import leafletoverpasslayer from 'leaflet-overpass-layer';
import leafletdraw from 'leaflet-draw';
import leafletterminator from 'leaflet-terminator/leaflet-terminator.js';
import leafletcoordinates from 'leaflet.coordinates/dist/Leaflet.Coordinates-0.1.5.min.js';
import leafletrotatedmarker from 'leaflet-rotatedmarker';
import leafleteasybutton from 'leaflet-easybutton';
import zoomslider from 'leaflet.zoomslider';
import contextmenu from 'leaflet-contextmenu'
//import leafletgrid from 'L.Grid';

import 'leaflet-easybutton/src/easy-button.css';
import 'leaflet.zoomslider/src/L.Control.Zoomslider.css';

class mapcomponent {
    
    constructor(scope, leafletData, objectproxy, $state, $rootScope, socket, user, schemata, menu, alert) {
        this.scope = scope;
        this.leaflet = leafletData;
        this.op = objectproxy;
        this.state = $state;
        this.rootscope = $rootScope;
        this.user = user;
        this.schemata = schemata;
        this.menu = menu;
        this.alert = alert;

        this.drawnLayer = '';
        this.map = '';
        this.host = socket.host;

        this.follow = false;
        this.followlayers = false;

        this.mapviewuuid = null;

        this.deviceinfo = {}; // TODO: Fix this one. Needs angular device detector service

        this.center = {
            lat: 0,
            lng: 0,
            zoom: 3,
            autoDiscover: true
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

        this.controls = {

            draw: {},
            scale: {}
        };

        this.showCoordinates = function(e) {
            $('#statusCenter').text(e.latlng);
        };

        this.centerMap = function(e) {
            self.map.panTo(e.latlng);
        };

        this.zoomIn = function() {
            self.map.zoomIn();
        };

        this.zoomOut = function() {
            self.map.zoomOut();
        };

        this.defaults = {
            map: {
                contextmenu: true,
                contextmenuWidth: 140,
                contextmenuItems: [{
                    text: 'Show coordinates',
                    callback: this.showCoordinates
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

        this.geojson = {};

        this.layers = {
            baselayers: {
                osm: {
                    name: 'OpenStreetMap',
                    type: 'xyz',
                    // url: 'http://{s}.tile.osm.org/{z}/{x}/{y}.png',
                    url: 'http://' + this.host + '/tilecache/a.tile.osm.org/{z}/{x}/{y}.png',
                    layerOptions: {
                        //subdomains: ['a', 'b', 'c'],
                        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
                        continuousWorld: false,
                        minZoom: 3
                    }
                }
            },
            overlays: {
                draw: {
                    name: 'draw',
                    type: 'group',
                    visible: true,
                    layerParams: {
                        showOnSelector: false
                    }
                }
            }
        };

        this.events = {
            map: {
                enable: ['moveend', 'dblclick', 'mousemove'],
                logic: 'emit'
            }
        };

        var self = this;

        this.scope.$on('OP.Get', function (event, objuuid, obj, schema) {
            console.log('[MAP] Object:', obj);
            if (objuuid === self.mapviewuuid) {
                self.updateMapview(objuuid);
                self.clearLayers();
            } else if (schema === 'geoobject') {
                console.log('I think this is relevant: ', obj);
            } else if (schema === 'layergroup') {
                console.log('Layergroup received:', obj);

                self.clearLayers();

                if (typeof obj.layers !== 'undefined') {
                    for (var layer of obj.layers) {
                        self.op.getObject('layer', layer);
                    }
                }
            } else if (schema === 'layer') {
                console.log('Received layer object: ', obj);
                self.addLayer(objuuid);
            }
        });

        this.clearLayers = function () {
            self.layers.baselayers = {};
            self.layers.overlays = {};
        };

        this.addLayer = function (uuid) {
            var layer = self.op.objects[uuid];
            layer.url = layer.url.replace(/hfoshost/, self.host);

            console.log('Adding layer:', layer);
            if (layer.baselayer === true) {
                self.layers.baselayers[layer.uuid] = layer;
            } else {
                self.layers.overlays[layer.uuid] = layer;
            }
        };

        this.removeLayer = function (uuid) {
            var layer = self.op.objects[uuid];
            console.log('Removing layer:', layer);
            if (layer.baselayer === true) {
                self.layers.baselayers.delete(uuid);
            } else {
                self.layers.overlays.delete(uuid);
            }
        };

        this.toggleLayer = function (state, uuid) {
            console.log('Oh, you selected layer:', state, uuid);
            if (state === true) {
                self.addLayer(uuid);
            } else {
                self.removeLayer(uuid);
            }
        };

        this.switchLayergroup = function (uuid) {
            console.log('Switching to new layergroup: ', uuid);
            self.op.getObject('layergroup', uuid);
        };

        this.switchMapview = function (uuid) {
            console.log('Switching to new mapview: ', uuid);
            self.mapviewuuid = uuid;
            self.op.getObject('mapview', uuid);
        };

        this.getLayergroups = function () {
            console.log('[MAP] Checking layergroups:', self.mapview);
            if (typeof self.mapview.layergroups !== 'undefined') {

                for (var group of self.mapview.layergroups) {
                    self.op.getObject('layergroup', group);
                }
            }
        };

        this.scope.$on('OP.ListUpdate', function (event, schema) {
            if (schema === 'geoobject') {
                var list = self.op.lists.geoobject;

                console.log('Map received a list of geoobjects: ', schema, list);

                for (var item of list) {
                    console.log('Item:', item);
                    console.log('Layer:', self.drawnLayer);


                    var myLayer = L.geoJson().addTo(self.map);
                    console.log('This strange thing:', myLayer);
                    myLayer.addData(item.geojson);

                    //self.drawnLayer.addData(item.geojson);
                }
            }
            if (schema === 'layergroup') {
                var grouplist = self.op.lists.layergroup;
                var layermenu = [];
                for (var group of grouplist) {
                    layermenu.push({
                        type: 'func',
                        name: group.uuid,
                        text: group.name,
                        callback: self.switchLayergroup,
                        args: group.uuid
                    });
                }
                self.menu.addMenu('Layergroups', layermenu);
            }
            if (schema === 'mapview') {
                var mapviewlist = self.op.lists.mapview;
                var mapviewmenu = [];
                for (var mapview of mapviewlist) {
                    mapviewmenu.push({
                        type: 'func',
                        name: mapview.uuid,
                        text: mapview.name,
                        callback: self.switchMapview,
                        args: mapview.uuid
                    });
                }
                self.menu.addMenu('Mapviews', mapviewmenu);
            }
        });

        this.scope.$on('OP.Update', function (event, objuuid) {
            if (objuuid === self.mapviewuuid) {
                self.updateMapview(objuuid);
                self.syncFromMapview();
            }
        });

        this.syncToMapview = function () {
            console.log('MAPVIEWUUID: ', self.mapviewuuid);
            if (self.mapviewuuid !== null) {
                self.mapview.coords = self.center;
                console.log('Sync to MV: ', self.mapview);
                if (self.sync) {
                    self.op.putObject('mapview', self.mapview);
                }
            }
        };

        this.updateMapview = function (objuuid) {
            if (objuuid === self.mapviewuuid) {
                console.log('[MAP] Received associated mapview.');
                self.mapview = self.op.objects[objuuid];
                if (self.followlayers === true) {
                    self.getLayergroups();
                }
            }
        };

        this.syncFromMapview = function () {
            if (self.mapviewuuid !== null) {
                self.center = self.mapview.coords;
                self.scope.$apply();
                console.log('Sync from MV: ', self.center);
            }
        };

        this.getGeoobjects = function () {
            console.log('Getting geoobjects');
            self.op.getList('geoobject', {'owner': self.user.useruuid}, ['geojson']);
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

        this.getMapdataLists = function () {
            console.log('[MAP] Getting available map data objects.');
            self.op.getList('layergroup');
            self.op.getList('mapview');
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

        var mapEvents = self.events.map.enable;

        var handleEvent = function (event) {
            if (self.user.signedin === true) {
                //console.log('Map Event:', event);
                if (event.name === 'leafletDirectiveMap.moveend') {
                    if (self.sync) {
                        console.log('Synchronizing map');
                        self.syncToMapview();
                    }
                } else if (event.name === 'leafletDirectiveMap.dblclick') {
                    console.log(self.layers);
                } else if (event.name === 'leafletDirectiveMap.mousemove') {
                    console.log(event);
                }
            }
        };

        for (var k of mapEvents) {
            var eventName = 'leafletDirectiveMap.' + k;
            this.scope.$on(eventName, function (event) {
                handleEvent(event);
            });
        }

        leafletData.getMap().then(function (map) {
            console.log('Setting up initial map settings.');
            self.map = map;

            map.on('click', function (e) {
                $('#statusCenter').html = 'Latitude: ' + e.latlng.lat + ' Longitude: ' + e.latlng.lng;
            });

            // Resize map to accomodate for statusbar
            //console.log('HEIGHTS:',  $('footer').height());
            //$('.angular-leaflet-map').height($('.angular-leaflet-map').height() - $('footer').height());

            map.setZoom(2);
            //map.panTo({lat: 52.513, lon: 13.41998});

            //if (self.deviceinfo.type !== 'mobile') {
            //    var Zoomslider = new L.Control.Zoomslider().addTo(map);
            //    $('.leaflet-control-zoom').css('visibility', 'hidden');
            //}

            self.terminator = leafletterminator()
                .setStyle({
                    weight: 1,
                    color: '#000',
                    fill: '#000'
                }).addTo(map);
            //var GraticuleOne = L.graticule({
            //    style: {color: '#55A', weight: 1, dashArray: '.'},
            //    interval: 1
            //}).addTo(map);

            //var grid = L.grid({redraw: 'moveend'}).addTo(map);
            //var MousePosition = L.control.mousePosition().addTo(map);
            //var PanControl = L.control.pan().addTo(map);
            self.courseplot = L.polyline([], {color: 'red'}).addTo(map);

            self.toggledraw = L.easyButton({
                id: 'btn_toggledraw',
                states: [{
                    stateName: 'disabled',
                    icon: 'fa-pencil',
                    onClick: function (control) {
                        self.drawing = true;
                        $('.leaflet-draw').show();
                        control.state('enabled');
                        $('#btn_toggledraw').attr('background', 'hotpink');
                    }
                }, {
                    stateName: 'enabled',
                    icon: 'fa-pencil',
                    onClick: function (control) {
                        self.drawing = false;
                        $('.leaflet-draw').hide();
                        control.state('disabled');
                        $('#btn_toggledraw').attr('background', 'white');
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
                            self.alert.add('warning', 'No mapview', 'There is no mapview selected that you could follow. Use the menu to select one.');
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
                            self.alert.add('warning', 'No mapview', 'There is no mapview selected that you could follow. Use the menu to select one.');
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

            self.toggledraw.addTo(map);
            self.togglefollow.addTo(map);
            self.togglesync.addTo(map);

            L.RotatedMarker = L.Marker.extend({
                options: {angle: 0},
                _setPos: function (pos) {
                    L.Marker.prototype._setPos.call(this, pos);
                    if (L.DomUtil.TRANSFORM) {
                        // use the CSS transform rule if available
                        this._icon.style[L.DomUtil.TRANSFORM] += ' rotate(' + this.options.angle + 'deg)';
                    } else if (L.Browser.ie) {
                        // fallback for IE6, IE7, IE8
                        var rad = this.options.angle * L.LatLng.DEG_TO_RAD,
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

            /*var Icons = {
             Vessel: L.icon({
             iconUrl: '/assets/images/icons/vessel.png',
             //shadowUrl: 'leaf-shadow.png',

             iconSize: [25, 25], // size of the icon
             //shadowSize:   [50, 64], // size of the shadow
             iconAnchor: [12, 12], // point of the icon which will correspond to marker's location
             //shadowAnchor: [4, 62],  // the same for the shadow
             popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
             }),
             VesselMoving: L.icon({
             iconUrl: '/assets/images/icons/vessel-moving.png',
             //shadowUrl: 'leaf-shadow.png',

             iconSize: [25, 25], // size of the icon
             //shadowSize:   [50, 64], // size of the shadow
             iconAnchor: [12, 12], // point of the icon which will correspond to marker's location
             //shadowAnchor: [4, 62],  // the same for the shadow
             popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
             }),
             VesselStopped: L.icon({
             iconUrl: '/assets/images/icons/vessel-stopped.png',
             //shadowUrl: 'leaf-shadow.png',

             iconSize: [25, 25], // size of the icon
             //shadowSize:   [50, 64], // size of the shadow
             iconAnchor: [12, 12], // point of the icon which will correspond to marker's location
             //shadowAnchor: [4, 62],  // the same for the shadow
             popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
             })
             };

             console.log("Rotated marker: ", L.rotatedMarker);
             var VesselMarker = L.rotatedMarker(self.vessel.coords, {icon: Icons.Vessel}).addTo(map);
             console.log("Vessel marker:", VesselMarker);
             */

            leafletData.getLayers().then(function (baselayers) {
                var drawnItems = baselayers.overlays.draw;
                self.drawnLayer = drawnItems;
                console.log('The basedrawlayer looks like this:', drawnItems);
                map.on('draw:created', function (e) {
                    var layer = e.layer;
                    console.log('Map drawing created:', e, ' layer:', layer);
                    drawnItems.addLayer(layer);

                    var geojson = layer.toGeoJSON();

                    console.log(geojson);

                    self.geojson = geojson;

                    var geoobject = {
                        uuid: 'create',
                        owner: self.user.useruuid,
                        geojson: geojson
                    };
                    self.op.putObject('geoobject', geoobject);
                });
            });

            $('.leaflet-draw').hide();

        })

        this.scope.$on('Profile.Update', function () {
            console.log('Profile update - fetching map data');
            self.requestMapData();
        });
        if (this.user.signedin === true) {
            console.log('Logged in - fetching map data');
            this.requestMapData();
        }

    }

}

mapcomponent.$inject = ['$scope', 'leafletData', 'objectproxy', '$state', '$rootScope', 'socket', 'user', 'schemata', 'menu', 'alert'];

export default mapcomponent;

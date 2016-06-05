'use strict';

import leafletoverpasslayer from 'leaflet-overpass-layer';
import leafletdraw from 'leaflet-draw';
import leafletterminator from 'leaflet-terminator/leaflet-terminator.js';
import leafletcoordinates from 'leaflet.coordinates/dist/Leaflet.Coordinates-0.1.5.min.js';
import leafletrotatedmarker from 'leaflet-rotatedmarker';
import leafleteasybutton from 'leaflet-easybutton';

class mapcomponent {

    constructor(scope, leafletData, objectproxy, $state, $rootScope, socket, user) {
        this.scope = scope;
        this.leaflet = leafletData;
        this.op = objectproxy;
        this.state = $state;
        this.rootscope = $rootScope;
        this.user = user;

        var host = socket.host;

        this.deviceinfo = {}; // TODO: Fix this one. Needs angular device detector service

        this.center = {
            lat: 0,
            lon: 0,
            zoom: 3,
            autoDiscover: true
        };

        this.vessel = {
            coords: {
                lat: 54.17825,
                lon: 7.88888
            },
            course: 0,
            speed: 0,
            radiorange: 700
        };

        this.controls = {
            draw: {},
            scale: {}
        };

        this.geojson = {};

        this.layers = {
            baselayers: {
                osm: {
                    name: 'OpenStreetMap',
                    type: 'xyz',
                    // url: 'http://{s}.tile.osm.org/{z}/{x}/{y}.png',
                    url: 'http://' + host + '/tilecache/a.tile.osm.org/{z}/{x}/{y}.png',
                    layerOptions: {
                        //subdomains: ['a', 'b', 'c'],
                        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
                        continuousWorld: false,
                        minZoom: 3
                    }
                },
                openseamap: {
                    name: 'OpenSeaMap',
                    type: 'xyz',
                    // http://c.tile.openstreetmap.org/{z}/{x}/{y}.png
                    url: 'http://' + host + '/tilecache/tiles.openseamap.org/seamark/{z}/{x}/{y}.png',
                    layerOptions: {
                        attribution: '&copy; OpenSeaMap contributors',
                        minZoom: 10,
                        maxZoom: 15
                    }
                },
                cycle: {
                    name: 'OpenCycleMap',
                    type: 'xyz',
                    url: 'http://' + host + '/tilecache/a.tile.opencyclemap.org/cycle/{z}/{x}/{y}.png',
                    layerOptions: {
                        //subdomains: ['a', 'b', 'c'],
                        attribution: '&copy; <a href="http://www.opencyclemap.org/copyright">OpenCycleMap</a> contributors - &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                        continuousWorld: true
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
                },
                openseamap: {
                    name: 'OpenSeaMap',
                    type: 'xyz',
                    // http://c.tile.openstreetmap.org/{z}/{x}/{y}.png
                    url: 'http://' + host + '/tilecache/t1.openseamap.org/seamark/{z}/{x}/{y}.png',
                    layerOptions: {
                        minZoom: 10,
                        maxZoom: 14,
                        attribution: '&copy; OpenSeaMap contributors'
                    }
                },
                openweathermap: {
                    name: 'OpenWeatherMap Clouds',
                    type: 'xyz',
                    url: 'http://' + host + '/tilecache/a.tile.openweathermap.org/map/clouds/{z}/{x}/{y}.png',
                    layerOptions: {
                        attribution: '&copy; OpenWeatherMap',
                        continuousWorld: true
                    }
                },

                hillshade: {
                    name: 'Hillshade Europa',
                    type: 'wms',
                    url: 'http://' + host + '/tilecache/129.206.228.72/cached/hillshade',
                    visible: false,
                    layerOptions: {
                        layers: 'europe_wms:hs_srtm_europa',
                        format: 'image/png',
                        opacity: 0.25,
                        attribution: 'Hillshade layer by GIScience http://www.osm-wms.de',
                        crs: L.CRS.EPSG900913
                    }
                },
                fire: {
                    name: 'OpenFireMap',
                    type: 'xyz',
                    url: 'http://' + host + '/tilecache/openfiremap.org/hytiles/{z}/{x}/{y}.png',
                    visible: false,
                    layerOptions: {
                        attribution: '&copy; <a href="http://www.openfiremap.org">OpenFireMap</a> contributors - &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                        continuousWorld: true
                    }
                },
                esriimagery: {
                    name: 'Satellite ESRI World Imagery',
                    type: 'xyz',
                    url: 'http://' + host + '/tilecache/server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    visible: false,
                    layerOptions: {
                        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                        continuousWorld: true,
                        opacity: 0.25
                    }
                }
            }
        };

        this.events = {
            map: {
                enable: ['moveend', 'dblclick'],
                logic: 'emit'
            }
        };

        var self = this;

        var mapEvents = self.events.map.enable;

        var handleEvent = function (event) {
            if (self.user.signedin) {
                console.log('Map Event:', event);
                if (event.name === 'leafletDirectiveMap.moveend') {
                    if (self.sync) {
                        console.log('Synchronizing map');
                        self.syncToMapview();
                    }
                } else if (event.name === 'leafletDirectiveMap.dblclick') {
                    var subscriptionuuid = prompt('Enter subscription uuid:');
                    if (subscriptionuuid !== '') {
                        self.objectproxy.get('mapview', subscriptionuuid);
                    }
                }
            }
        };

        for (var k in mapEvents) {
            var eventName = 'leafletDirectiveMap.' + mapEvents[k];
            this.scope.$on(eventName, function (event) {
                handleEvent(event);
            });
        }


        leafletData.getMap().then(function (map) {
            console.log('Setting up initial map settings.');
            map.setZoom(2);
            //map.panTo({lat: 52.513, lon: 13.41998});

            if (self.deviceinfo.type !== 'mobile') {
                //var Zoomslider = new L.Control.Zoomslider().addTo(map);
                //$('.leaflet-control-zoom').css('visibility', 'hidden');
            }

            //var Terminator = terminator().addTo(map);
            //var GraticuleOne = L.graticule({
            //    style: {color: '#55A', weight: 1, dashArray: '.'},
            //    interval: 1
            //}).addTo(map);
            //var MousePosition = L.control.mousePosition().addTo(map);
            //var PanControl = L.control.pan().addTo(map);
            var courseplot = L.polyline([], {color: 'red'}).addTo(map);

            var togglefollow = L.easyButton({
                id: 'btn_togglefollow',
                states: [{
                    stateName: 'following',
                    icon: 'fa-eye',
                    onClick: function (control) {
                        self.follow = false;
                        unsubscribe();
                        control.state('static');
                    }
                }, {
                    stateName: 'static',
                    icon: 'fa-eye-slash',
                    onClick: function (control) {
                        self.follow = true;
                        subscribe();
                        control.state('following');
                    }
                }],
                title: 'Toggle map following'
            });

            var togglesync = L.easyButton({
                id: 'btn_togglesync',
                states: [{
                    stateName: 'synchronized',
                    icon: 'fa-chain',
                    onClick: function (control) {
                        console.log('[MAP] Disabling synchronization');
                        self.sync = false;
                        control.state('unsynchronized');
                    }
                }, {
                    stateName: 'unsynchronized',
                    icon: 'fa-chain-broken',
                    onClick: function (control) {
                        console.log('[MAP] Enabling synchronization');
                        self.sync = true;
                        control.state('synchronized');
                    }
                }],
                title: 'Toggle synchronization to ship'
            });

            var selectView = L.easyButton({
                id: 'btn_selectview',
                states: [{
                    stateName: 'select',
                    icon: 'fa-list-alt',
                    onClick: function (control) {
                        console.log('[MAP] Triggering view selection');
                        SelectView();

                    }
                }],
                title: 'Select a view'
            });

            togglefollow.addTo(map);
            togglesync.addTo(map);
            selectView.addTo(map);


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

            var Icons = {
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
            var VesselMarker = L.rotatedMarker(self.vessel.coords, {icon: Icons.vessel}).addTo(map);
            console.log("Vessel marker:", VesselMarker);

            leafletData.getLayers().then(function (baselayers) {
                var drawnItems = baselayers.overlays.draw;
                map.on('draw:created', function (e) {
                    var layer = e.layer;
                    drawnItems.addLayer(layer);

                    var geojson = layer.toGeoJSON();

                    console.log(geojson);

                    self.geojson = geojson;
                    socket.send(geojson);

                });
            });
        })
    }
}

mapcomponent.$inject = ['$scope', 'leafletData', 'objectproxy', '$state', '$rootScope', 'socket', 'user'];

export default mapcomponent;

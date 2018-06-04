import './map/map.scss';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import 'leaflet.coordinates/dist/Leaflet.Coordinates-0.1.5.css';
import 'leaflet-contextmenu/dist/leaflet.contextmenu.css';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import leafletdirective from 'angular-leaflet-directive';

import { routing } from './map.config.js';

import mapcomponent from './map/components/map.js';
import maptemplate from './map/components/map.tpl.html';
import mapservice from './map/services/map.service';

export default angular
    .module('main.app.map', ['leaflet-directive', uirouter])
    .config(routing)
    .service('mapservice', mapservice)
    .component('map', {controller: mapcomponent, template: maptemplate})
    .name;

import './map/map.scss';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import 'leaflet.coordinates/dist/Leaflet.Coordinates-0.1.5.css';
import 'leaflet-contextmenu/dist/leaflet.contextmenu.css';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import leafletdirective from 'angular-leaflet-directive';

import { routing } from './map.config.js';

import mapcomponent from './map/map.js';
import template from './map/map.tpl.html';

export default angular
    .module('main.app.map', ['leaflet-directive', uirouter])
    .config(routing)
    .component('map', {controller: mapcomponent, template: template})
    .name;

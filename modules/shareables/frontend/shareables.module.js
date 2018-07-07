import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './shareables.config.js';

import shareablescomponent from './shareables/shareables.js';
import template from './shareables/shareables.tpl.html';

import 'angular-bootstrap-calendar/dist/css/angular-bootstrap-calendar.css';
import ngcalendar from 'angular-bootstrap-calendar';

export default angular
    .module('main.app.shareables', [uirouter, 'mwl.calendar', 'ngAnimate'])
    .config(routing)
    .component('shareables', {controller: shareablescomponent, template: template})
    .name;

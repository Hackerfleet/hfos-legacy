import './dashboard/dashboard.scss';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './dashboard.config.js';

import dashboardcomponent from './dashboard/dashboard';
import digitalreadout from './dashboard/controllers/digitalreadout';

import template from './dashboard/dashboard.tpl.html';
import digitalreadouttemplate from './dashboard/templates/digitalreadout.tpl.html';

import dynamiccontroller from './dashboard/directives/dynamiccontroller.js';

export default angular
    .module('main.app.dashboard', [uirouter])
    .config(routing)
    .component('dashboard', {controller: dashboardcomponent, template: template})
    .component('digitalreadout', {controller: digitalreadout, template: digitalreadouttemplate})
    .directive('dynamiccontroller', {directive: dynamiccontroller})
    .name;

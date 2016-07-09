import './dashboard/dashboard.scss';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './dashboard.config.js';

import dashboardcomponent from './dashboard/dashboard';

import digitalreadout from './dashboard/controllers/digitalreadout';
import simplebarreadout from './dashboard/controllers/simplebarreadout';

import template from './dashboard/dashboard.tpl.html';

import dynamiccontroller from './dashboard/directives/dynamiccontroller.js';

export default angular
    .module('main.app.dashboard', [uirouter])
    .config(routing)
    .component('dashboard', {controller: dashboardcomponent, template: template})
    .controller('digitalreadout', digitalreadout)
    .controller('simplebarreadout', simplebarreadout)
    .directive('ngDynamicController', dynamiccontroller)
    .name;

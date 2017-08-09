import './dashboard/dashboard.scss';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './dashboard.config.js';

import dashboardcomponent from './dashboard/dashboard';

import digitalreadout from './dashboard/controllers/digitalreadout';
import simplebarreadout from './dashboard/controllers/simplebarreadout';
import historybarreadout from './dashboard/controllers/historybarreadout';
import simplecompass from './dashboard/controllers/simplecompass';
import linechart from './dashboard/controllers/linechart';

import template from './dashboard/dashboard.tpl.html';

import dynamiccontroller from './dashboard/directives/dynamiccontroller.js';

require('c3/c3.css');
require('d3');
require('c3');
require('angular-chart');


export default angular
    .module('main.app.dashboard', [uirouter, 'angularChart'])
    .config(routing)
    .component('dashboard', {controller: dashboardcomponent, template: template, bindings: {uuid: '@', hideui: '@'}})
    .controller('digitalreadout', digitalreadout)
    .controller('simplebarreadout', simplebarreadout)
    .controller('historybarreadout', historybarreadout)
    .controller('simplecompass', simplecompass)
    .controller('linechart', linechart)
    .directive('ngDynamicController', dynamiccontroller)
    .name;

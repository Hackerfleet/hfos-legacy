import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './taskgrid.config.js';

import taskgridcomponent from './taskgrid/taskgrid.js';
import template from './taskgrid/taskgrid.tpl.html';

export default angular
    .module('main.app.taskgrid', [uirouter])
    .config(routing)
    .component('taskgrid', {controller: taskgridcomponent, template: template})
    .name;

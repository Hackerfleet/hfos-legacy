import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './robot.config.js';

import remotecontrolcomponent from './remotecontrol/remotecontrol.js';
import template from './remotecontrol/remotecontrol.tpl.html';

export default angular
    .module('main.app.remotecontrol', [uirouter])
    .config(routing)
    .component('remotecontrol', {controller: remotecontrolcomponent, template: template})
    .name;

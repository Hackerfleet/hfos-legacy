import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './garden.config.js';

import gardencomponent from './garden/garden.js';
import template from './garden/garden.tpl.html';

export default angular
    .module('main.app.garden', [uirouter])
    .config(routing)
    .component('garden', {controller: gardencomponent, template: template})
    .name;

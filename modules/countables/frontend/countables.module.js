import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './countables.config.js';

import countablescomponent from './countables/countables.js';
import template from './countables/countables.tpl.html';

export default angular
    .module('main.app.countables', [uirouter])
    .config(routing)
    .component('countables', {controller: countablescomponent, template: template})
    .name;

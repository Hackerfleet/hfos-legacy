import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './library.config.js';

import librarycomponent from './library/library.js';
import template from './library/library.tpl.html';

export default angular
    .module('main.app.library', [uirouter])
    .config(routing)
    .component('library', {controller: librarycomponent, template: template})
    .name;

import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './wiki.config.js';

import wikicomponent from './wiki/wiki.js';
import template from './wiki/wiki.tpl.html';

export default angular
    .module('main.app.wiki', [uirouter])
    .config(routing)
    .component('wiki', {controller: wikicomponent, template: template})
    .name;

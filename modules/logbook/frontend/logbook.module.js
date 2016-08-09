import './logbook/logbook.scss';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './logbook.config.js';

import logbookcomponent from './logbook/logbook';
import template from './logbook/logbook.tpl.html';

export default angular
    .module('main.app.logbook', [uirouter])
    .config(routing)
    .component('logbook', {controller: logbookcomponent, template: template})
    .name;

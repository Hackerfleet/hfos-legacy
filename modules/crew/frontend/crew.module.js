import './crew/crewmanagement.scss';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './crew.config.js';

import rostercomponent from './crew/roster';
import template from './crew/roster.tpl.html';

export default angular
    .module('main.app.crew', [uirouter])
    .config(routing)
    .component('crew', {controller: rostercomponent, template: template})
    .name;

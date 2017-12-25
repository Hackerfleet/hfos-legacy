import './contacts/contactmanagement.scss';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './contacts.config.js';

import rostercomponent from './contacts/roster';
import template from './contacts/roster.tpl.html';

export default angular
    .module('main.app.contact', [uirouter])
    .config(routing)
    .component('contact', {controller: rostercomponent, template: template})
    .name;

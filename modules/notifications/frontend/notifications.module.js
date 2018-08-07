import './notifications/notifications.scss';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './notifications.config.js';

import notificationcomponent from './notifications/notifications';
import template from './notifications/notifications.tpl.html';

export default angular
    .module('main.app.notifications', [uirouter])
    .config(routing)
    .component('notifications', {controller: notificationcomponent, template: template})
    .name;

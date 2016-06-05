import './chat/chat.scss';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './chat.config.js';

import chatcomponent from './chat/chat';
import customwidget from './chat/customwidget';

import template from './chat/chat.tpl.html';

export default angular
    .module('main.app.chat', [uirouter])
    .config(routing)
    .component('chat', {controller: chatcomponent, template: template})
    .name;

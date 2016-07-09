//import './chat/chat.scss';

import angular from 'angular';
import uirouter from 'angular-ui-router';

import { routing } from './chat.config.js';

import chatservice from './chat/chatservice.js';
import chatcomponent from './chat/chatcomponent.js';

import template from './chat/chat.tpl.html';

export default angular
    .module('main.app.chat', [uirouter])
    .config(routing)
    .service('chatservice', chatservice)
    .component('chat', {controller: chatcomponent, template: template})
    .name;
